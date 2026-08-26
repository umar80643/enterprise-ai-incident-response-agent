from datetime import UTC, datetime
from pathlib import Path

from app.core.errors import NotFoundError
from app.rag.chunking import ingest_tree
from app.repositories.store import store


class RepositoryService:
    async def index(self, name, path, branch):
        root = Path(path).resolve()
        if not root.exists() or not root.is_dir():
            raise NotFoundError("Repository path not found")
        chunks = ingest_tree(root)
        repo = {
            "id": name,
            "name": name,
            "path": str(root),
            "branch": branch,
            "status": "READY",
            "chunk_count": len(chunks),
            "indexed_at": datetime.now(UTC).isoformat(),
        }
        await store.put("repositories", name, repo)
        return repo

    def status(self, repo_id):
        repo = store.get("repositories", repo_id)
        if not repo:
            raise NotFoundError("Repository not found")
        return repo


repository_service = RepositoryService()
