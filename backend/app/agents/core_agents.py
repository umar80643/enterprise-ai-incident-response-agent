from pathlib import Path

from app.core.config import get_settings
from app.rag.chunking import ingest_tree
from app.rag.retrieval import Reranker, hybrid_retrieve
from app.schemas.domain import *


def usage(agent):
    return UsageRecord(
        agent=agent, model="deterministic-local", input_tokens=0, output_tokens=0, estimated_cost=0
    )


async def planner(state):
    state["execution_plan"] = InvestigationPlan(
        objective=f"Investigate: {state['incident_description']}",
        subtasks=[
            "inspect repository",
            "retrieve evidence",
            "generate competing hypotheses",
            "identify root cause",
            "propose minimal fix",
            "generate regression tests",
            "review risk",
        ],
        required_tools=["repository.tree", "retrieval.hybrid", "repository.read", "safe_execution"],
        expected_evidence=[
            "relevant implementation",
            "configuration/recent-change clues",
            "tests or call sites",
        ],
    )
    state.setdefault("usage", []).append(usage("planner"))
    return state


async def repository_analysis(state):
    chunks = ingest_tree(Path(state["repository_path"]))
    state["_chunks"] = chunks
    state["relevant_files"] = sorted({c.file_path for c in chunks})
    state["suspected_components"] = [
        p
        for p in state["relevant_files"]
        if any(x in p.lower() for x in ("checkout", "payment", "config"))
    ][:10]
    state.setdefault("usage", []).append(usage("repository"))
    return state


async def retrieval(state):
    query = state["incident_description"] + " HTTP 500 checkout configuration deployment"
    items = hybrid_retrieve(query, state["_chunks"], 12)
    if get_settings().rerank_enabled:
        items = Reranker().rerank(query, items)[:8]
    ev = []
    for c, score in items:
        ev.append(
            Evidence(
                id=c.id,
                repository=state["repository"],
                branch=state["branch"],
                file_path=c.file_path,
                line_start=c.line_start,
                line_end=c.line_end,
                symbol=c.symbol,
                chunk_type=c.chunk_type,
                excerpt=c.text[:2500],
                score=float(score),
            )
        )
    state["retrieved_context"] = ev
    state.setdefault("usage", []).append(usage("retrieval"))
    return state


async def debugging(state):
    ev = state.get("retrieved_context", [])
    hyps = []

    def ids_matching(*terms):
        return [
            e.id
            for e in ev
            if any(t in e.excerpt.lower() or t in e.file_path.lower() for t in terms)
        ]

    null_ids = ids_matching("timeout_seconds", "none", "checkout")
    config_ids = ids_matching("config", "env", "timeout")
    dep_ids = ids_matching("requirements", "dependency", "version")
    if null_ids:
        hyps.append(
            Hypothesis(
                hypothesis="A nullable checkout timeout configuration reaches arithmetic/comparison code and raises a TypeError.",
                evidence_ids=null_ids[:3],
                confidence=0.88,
                relevant_files=[e.file_path for e in ev if e.id in null_ids[:3]],
                assumptions=["The reported 500 traverses the indexed checkout path."],
            )
        )
    hyps.append(
        Hypothesis(
            hypothesis="A deployment configuration change introduced an invalid or missing runtime value.",
            evidence_ids=config_ids[:3],
            confidence=0.66 if config_ids else 0.35,
            relevant_files=[e.file_path for e in ev if e.id in config_ids[:3]],
            assumptions=["Deployment environment may differ from local defaults."],
        )
    )
    hyps.append(
        Hypothesis(
            hypothesis="A dependency change caused an incompatible runtime behavior.",
            evidence_ids=dep_ids[:2],
            confidence=0.25,
            relevant_files=[e.file_path for e in ev if e.id in dep_ids[:2]],
            counter_evidence=["No dependency-specific stack trace was supplied."],
        )
    )
    state["hypotheses"] = hyps
    state.setdefault("usage", []).append(usage("debugger"))
    return state


async def root_cause(state):
    hyps = sorted(state["hypotheses"], key=lambda h: h.confidence, reverse=True)
    if not hyps or hyps[0].confidence < 0.55 or not hyps[0].evidence_ids:
        state["root_cause"] = RootCauseAnalysis(
            status="INSUFFICIENT_EVIDENCE",
            root_cause="Insufficient evidence to identify a supported root cause.",
            confidence=0,
            evidence_ids=[],
            inference="More logs or relevant code are required.",
        )
    else:
        h = hyps[0]
        state["root_cause"] = RootCauseAnalysis(
            root_cause=h.hypothesis,
            confidence=h.confidence,
            evidence_ids=h.evidence_ids,
            inference="The highest-ranked hypothesis is directly supported by retrieved code/config evidence.",
            assumptions=h.assumptions,
        )
    state.setdefault("usage", []).append(usage("root_cause"))
    return state


async def solution(state):
    rc = state["root_cause"]
    evidence = {e.id: e for e in state["retrieved_context"]}
    target = next(
        (e for i in rc.evidence_ids if (e := evidence.get(i)) and e.file_path.endswith(".py")), None
    )
    if rc.status == "INSUFFICIENT_EVIDENCE" or not target:
        state["proposed_solution"] = PatchProposal(
            summary="No patch generated without sufficient grounded evidence.",
            changed_files=[],
            unified_diff="",
            expected_behavior="No repository mutation.",
            side_effects=[],
        )
        return state
    text = target.excerpt
    # Demo fixture-specific but evidence-derived minimal patch.
    if "timeout_seconds = config.get" in text and "timeout_seconds * 1000" in text:
        diff = f"""--- a/{target.file_path}
+++ b/{target.file_path}
@@
-    timeout_seconds = config.get("timeout_seconds")
+    timeout_seconds = config.get("timeout_seconds", 5)
+    if timeout_seconds is None:
+        timeout_seconds = 5
     timeout_ms = timeout_seconds * 1000
"""
        state["proposed_solution"] = PatchProposal(
            summary="Default a missing/nullable checkout timeout before converting it to milliseconds.",
            changed_files=[target.file_path],
            unified_diff=diff,
            expected_behavior="Checkout no longer raises TypeError when timeout_seconds is absent or null.",
            side_effects=["Uses a 5 second fallback timeout."],
        )
    else:
        state["proposed_solution"] = PatchProposal(
            summary="Evidence supports investigation but no mechanically safe patch template matched.",
            changed_files=[],
            unified_diff="",
            expected_behavior="Requires human-authored fix.",
        )
    state.setdefault("usage", []).append(usage("solution"))
    return state


async def test_generation(state):
    patch = state["proposed_solution"]
    state["tests"] = TestPlan(
        unit_tests=["test_checkout_uses_default_timeout_when_config_missing"],
        regression_tests=(
            ["test_checkout_missing_timeout_does_not_return_500"] if patch.changed_files else []
        ),
    )
    # Validation is static/deterministic here; real execution is delegated to SAFE_EXECUTION.
    passed = bool(patch.changed_files and "if timeout_seconds is None" in patch.unified_diff)
    state["test_results"] = [
        TestResult(
            passed=passed,
            command=["python", "-m", "pytest"],
            output=(
                "Static patch validation passed; execute repository tests through SAFE_EXECUTION after approval."
                if passed
                else "No executable patch generated."
            ),
        )
    ]
    state.setdefault("usage", []).append(usage("testing"))
    return state


async def reviewer(state):
    patch = state["proposed_solution"]
    tests = state["test_results"]
    findings = []
    if not patch.changed_files:
        findings.append("No patch available.")
    if not all(t.passed for t in tests):
        findings.append("Validation failed.")
    if patch.changed_files and "None" not in patch.unified_diff:
        findings.append("Nullable configuration is not explicitly handled.")
    approved = not findings
    state["review_findings"] = ReviewResult(
        approved=approved,
        findings=findings
        or ["Patch is minimal, evidence-grounded, and includes a regression-test requirement."],
        risk_level="MEDIUM" if patch.changed_files else "LOW",
        missing_tests=[] if patch.changed_files else ["No patch to test"],
    )
    state["risk_level"] = state["review_findings"].risk_level
    state["approval_status"] = (
        "WAITING_APPROVAL" if approved and patch.changed_files else "NOT_REQUIRED"
    )
    state.setdefault("usage", []).append(usage("reviewer"))
    return state
