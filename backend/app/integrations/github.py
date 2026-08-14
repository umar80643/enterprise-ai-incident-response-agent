import hashlib, hmac
from app.core.config import get_settings
from app.security.permissions import PermissionGuard
from app.schemas.domain import Permission

def verify_webhook(body:bytes, signature:str|None)->bool:
    secret=get_settings().github_webhook_secret.encode()
    expected="sha256="+hmac.new(secret,body,hashlib.sha256).hexdigest()
    return bool(signature and hmac.compare_digest(expected,signature))

class GitHubAdapter:
    def __init__(self,guard:PermissionGuard): self.guard=guard
    async def create_pr(self,investigation_id:str, patch:str):
        self.guard.require(Permission.CREATE_PR)
        s=get_settings()
        if not s.github_write_enabled:
            return {"mode":"simulation","branch":f"ai-fix/{investigation_id[:8]}","status":"SIMULATED","message":"GitHub writes disabled; no network mutation performed."}
        if not s.github_token:
            raise RuntimeError("GITHUB_WRITE_ENABLED=true but GITHUB_TOKEN is missing")
        raise RuntimeError("Real GitHub network adapter requires organization/repository coordinates; simulation is the safe default.")
