import logging
import re

import structlog

_SECRET = re.compile(r"(token|secret|authorization|api[_-]?key)", re.IGNORECASE)


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ]
    )


def safe_fields(**kwargs):
    return {k: ("[REDACTED]" if _SECRET.search(k) else v) for k, v in kwargs.items()}
