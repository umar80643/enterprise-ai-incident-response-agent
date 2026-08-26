import pytest

from app.core.errors import PermissionDenied
from app.schemas.domain import Permission
from app.security.permissions import PermissionGuard


def test_write_requires_permission():
    with pytest.raises(PermissionDenied):
        PermissionGuard({Permission.READ_ONLY}).require(Permission.CREATE_PR)
