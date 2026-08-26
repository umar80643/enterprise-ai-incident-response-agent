import asyncio
import time
from pathlib import Path

from app.schemas.domain import Permission, TestResult
from app.security.permissions import PermissionGuard

ALLOWED = {"pytest", "python"}


async def safe_run(
    command: list[str], cwd: str, guard: PermissionGuard, timeout: int = 30
) -> TestResult:
    guard.require(Permission.SAFE_EXECUTION)
    if not command or command[0] not in ALLOWED:
        raise ValueError("Command is not allowlisted")
    start = time.perf_counter()
    proc = await asyncio.create_subprocess_exec(
        *command,
        cwd=str(Path(cwd).resolve()),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except TimeoutError:
        proc.kill()
        await proc.wait()
        return TestResult(
            passed=False,
            command=command,
            output="Timed out",
            duration_ms=int((time.perf_counter() - start) * 1000),
        )
    return TestResult(
        passed=proc.returncode == 0,
        command=command,
        output=out.decode(errors="ignore")[-6000:],
        duration_ms=int((time.perf_counter() - start) * 1000),
    )
