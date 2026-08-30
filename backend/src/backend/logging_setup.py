"""
Central logging for the backend.

Everything worth keeping - request outcomes (PASS / FAIL), handled errors, and
unhandled exceptions with tracebacks - goes to `backend/log.txt` (rotating, so
it never grows unbounded) and also to the console.

Import `log` from here anywhere:

    from backend.logging_setup import log
    log.info("...")
    log.exception("...")   # inside an except block - includes the traceback
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# src/backend/logging_setup.py -> parents[2] == the backend/ project root,
# so the file lands next to pyproject.toml no matter what the cwd is.
LOG_PATH = Path(__file__).resolve().parents[2] / "log.txt"

_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def _build_logger() -> logging.Logger:
    logger = logging.getLogger("copycat")

    if logger.handlers:  # already configured (reload / re-import)
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(_FORMAT)

    file_handler = RotatingFileHandler(
        LOG_PATH,
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


log = _build_logger()
