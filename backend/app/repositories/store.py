import asyncio, json
from pathlib import Path
from typing import Any

class Store:
    """Development durable store. Production deployment swaps this behind the same service boundary for SQLAlchemy/Postgres."""
    def __init__(self, path: str = "./enterprise_store.json"):
        self.path = Path(path)
        self.lock = asyncio.Lock()
        self.data: dict[str, Any] = {"repositories":{}, "investigations":{}, "events":{}, "evidence":{}, "usage":{}, "approvals":{}, "audit":[]}
        if self.path.exists():
            try: self.data.update(json.loads(self.path.read_text()))
            except Exception: pass
    async def save(self):
        async with self.lock:
            self.path.write_text(json.dumps(self.data, indent=2, default=str))
    async def put(self, bucket: str, key: str, value: Any):
        self.data.setdefault(bucket,{})[key] = value
        await self.save()
    def get(self, bucket: str, key: str, default=None):
        return self.data.get(bucket,{}).get(key, default)
    def values(self, bucket: str):
        b=self.data.get(bucket,{})
        return list(b.values()) if isinstance(b,dict) else list(b)

store = Store()
