from app.schemas.domain import Permission
from app.core.errors import PermissionDenied

class PermissionGuard:
    def __init__(self, granted: set[Permission]):
        self.granted = granted
    def require(self, permission: Permission) -> None:
        if permission not in self.granted:
            raise PermissionDenied(f"Missing permission: {permission}")
