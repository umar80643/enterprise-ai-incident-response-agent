from abc import ABC, abstractmethod


class VectorStore(ABC):
    @abstractmethod
    async def upsert(self, chunks): ...
    @abstractmethod
    async def search(self, query, filters=None, limit=10): ...
    @abstractmethod
    async def delete_repository(self, repository): ...
    @abstractmethod
    async def health(self): ...


class LocalVectorStore(VectorStore):
    def __init__(self):
        self.chunks = []

    async def upsert(self, chunks):
        self.chunks.extend(chunks)

    async def search(self, query, filters=None, limit=10):
        from app.rag.retrieval import hybrid_retrieve

        return hybrid_retrieve(query, self.chunks, limit)

    async def delete_repository(self, repository):
        self.chunks = []

    async def health(self):
        return {"status": "ok", "backend": "local", "chunks": len(self.chunks)}
