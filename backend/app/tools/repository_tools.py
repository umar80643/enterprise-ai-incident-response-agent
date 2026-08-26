from pathlib import Path

from app.schemas.domain import Permission
from app.security.paths import safe_repo_path
from app.security.permissions import PermissionGuard


class RepositoryTools:
    def __init__(self, root: str, guard: PermissionGuard):
        self.root = root
        self.guard = guard

    def tree(self):
        self.guard.require(Permission.READ_ONLY)
        return [
            str(p.relative_to(self.root))
            for p in Path(self.root).rglob("*")
            if p.is_file() and ".git" not in p.parts
        ][:1000]

    def read(self, path: str):
        self.guard.require(Permission.READ_ONLY)
        return safe_repo_path(self.root, path).read_text(encoding="utf-8", errors="ignore")
