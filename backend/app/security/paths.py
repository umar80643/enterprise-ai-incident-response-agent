from pathlib import Path
from app.core.errors import PermissionDenied

def safe_repo_path(root: str | Path, requested: str | Path) -> Path:
    base = Path(root).resolve()
    candidate = (base / requested).resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise PermissionDenied("Path escapes registered repository root") from exc
    return candidate
