from contextlib import contextmanager
from time import perf_counter


@contextmanager
def timed():
    start = perf_counter()
    result = {"latency_ms": 0}
    try:
        yield result
    finally:
        result["latency_ms"] = int((perf_counter() - start) * 1000)
