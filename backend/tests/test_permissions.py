import pytest
from app.security.permissions import PermissionGuard
from app.schemas.domain import Permission
from app.core.errors import PermissionDenied
def test_write_requires_permission():
    with pytest.raises(PermissionDenied): PermissionGuard({Permission.READ_ONLY}).require(Permission.CREATE_PR)
