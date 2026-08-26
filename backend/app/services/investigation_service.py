import uuid
from datetime import UTC, datetime

from app.core.errors import NotFoundError
from app.graph.workflow import graph
from app.integrations.github import GitHubAdapter
from app.repositories.store import store
from app.schemas.domain import Permission
from app.security.permissions import PermissionGuard


class InvestigationService:
    async def _event(self, iid, event, payload=None):
        events = store.get("events", iid, []) or []
        events.append(
            {"event": event, "payload": payload or {}, "at": datetime.now(UTC).isoformat()}
        )
        await store.put("events", iid, events)

    async def create(self, repo_id, title, description, branch):
        repo = store.get("repositories", repo_id)
        if not repo:
            raise NotFoundError("Repository not found")
        iid = str(uuid.uuid4())
        record = {
            "id": iid,
            "repository_id": repo_id,
            "title": title,
            "description": description,
            "status": "RUNNING",
            "created_at": datetime.now(UTC).isoformat(),
        }
        await store.put("investigations", iid, record)
        await self._event(iid, "Planning investigation...")
        state = {
            "request_id": str(uuid.uuid4()),
            "session_id": iid,
            "investigation_id": iid,
            "repository": repo_id,
            "repository_path": repo["path"],
            "branch": branch,
            "issue": title,
            "incident_description": description,
            "step_count": 0,
            "solution_retries": 0,
            "execution_errors": [],
            "timestamps": {},
        }
        result = await graph.ainvoke(state)
        # Remove non-serializable/internal chunks before persistence.
        result.pop("_chunks", None)
        serial = {
            k: (
                v.model_dump()
                if hasattr(v, "model_dump")
                else (
                    [x.model_dump() if hasattr(x, "model_dump") else x for x in v]
                    if isinstance(v, list)
                    else v
                )
            )
            for k, v in result.items()
        }
        record.update(
            {
                "status": (
                    "WAITING_APPROVAL"
                    if result.get("approval_status") == "WAITING_APPROVAL"
                    else "SUCCESS"
                ),
                "result": serial,
            }
        )
        await store.put("investigations", iid, record)
        await store.put(
            "evidence",
            iid,
            [
                e.model_dump() if hasattr(e, "model_dump") else e
                for e in result.get("retrieved_context", [])
            ],
        )
        await store.put(
            "usage",
            iid,
            [u.model_dump() if hasattr(u, "model_dump") else u for u in result.get("usage", [])],
        )
        for msg in [
            "Analyzing repository...",
            "Searching indexed chunks...",
            "Generating hypotheses...",
            "Identifying root cause...",
            "Generating proposed solution...",
            "Validating proposed solution...",
            "Review complete.",
        ]:
            await self._event(iid, msg)
        if record["status"] == "WAITING_APPROVAL":
            await self._event(iid, "Awaiting human approval...")
        return record

    def get(self, iid):
        r = store.get("investigations", iid)
        if not r:
            raise NotFoundError("Investigation not found")
        return r

    def events(self, iid):
        self.get(iid)
        return store.get("events", iid, [])

    def evidence(self, iid):
        self.get(iid)
        return store.get("evidence", iid, [])

    def usage(self, iid):
        self.get(iid)
        return store.get("usage", iid, [])

    async def approve(self, iid, comment=None):
        r = self.get(iid)
        if r["status"] != "WAITING_APPROVAL":
            raise ValueError("Investigation is not awaiting approval")
        await store.put(
            "approvals",
            iid,
            {
                "decision": "APPROVE",
                "comment": comment,
                "at": datetime.now(UTC).isoformat(),
            },
        )
        patch = r["result"].get("proposed_solution", {}).get("unified_diff", "")
        gh = GitHubAdapter(PermissionGuard({Permission.CREATE_PR}))
        pr = await gh.create_pr(iid, patch)
        r["status"] = "SUCCESS"
        r["pull_request"] = pr
        await store.put("investigations", iid, r)
        await self._event(iid, "Approved; GitHub PR action completed.", pr)
        return r

    async def reject(self, iid, comment=None):
        r = self.get(iid)
        r["status"] = "REJECTED"
        await store.put("approvals", iid, {"decision": "REJECT", "comment": comment})
        await store.put("investigations", iid, r)
        await self._event(iid, "Rejected by human reviewer.")
        return r

    async def request_changes(self, iid, comment):
        r = self.get(iid)
        r["status"] = "WAITING_APPROVAL"
        await store.put("approvals", iid, {"decision": "REQUEST_CHANGES", "comment": comment})
        await self._event(iid, "Changes requested.", {"comment": comment})
        return r


investigation_service = InvestigationService()
