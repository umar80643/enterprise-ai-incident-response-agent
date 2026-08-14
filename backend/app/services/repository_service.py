from pathlib import Path
from datetime import datetime, timezone
from app.repositories.store import store
from app.rag.chunking import ingest_tree
from app.core.errors import NotFoundError

class RepositoryService:
    async def index(self,name,path,branch):
        root=Path(path).resolve()
        if not root.exists() or not root.is_dir(): raise NotFoundError("Repository path not found")
        chunks=ingest_tree(root)
        repo={"id":name,"name":name,"path":str(root),"branch":branch,"status":"READY","chunk_count":len(chunks),"indexed_at":datetime.now(timezone.utc).isoformat()}
        await store.put("repositories",name,repo)
        return repo
    def status(self,repo_id):
        repo=store.get("repositories",repo_id)
        if not repo: raise NotFoundError("Repository not found")
        return repo
repository_service=RepositoryService()
