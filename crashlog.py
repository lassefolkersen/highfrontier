"""Crash logging helpers for High Frontier startup and background threads."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys
import threading
from typing import Callable, TypeVar

_LOGGER_NAME = "highfrontier"
_HANDLER_MARKER = "_highfrontier_crashlog_handler"
T = TypeVar("T")


def log_dir_from_environment() -> Path:
    configured = os.environ.get("HIGHFRONTIER_LOG_DIR")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".highfrontier" / "logs"


def configure_logging(log_dir: str | os.PathLike[str] | None = None) -> Path:
    """Configure rotating file logging and return the active log file path."""
    directory = Path(log_dir).expanduser() if log_dir is not None else log_dir_from_environment()
    directory.mkdir(parents=True, exist_ok=True)
    log_file = directory / "highfrontier.log"

    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        if getattr(handler, _HANDLER_MARKER, False):
            root_logger.removeHandler(handler)
            handler.close()

    handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    setattr(handler, _HANDLER_MARKER, True)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s [%(threadName)s] %(name)s: %(message)s"
        )
    )
    handler.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    root_logger.setLevel(min(root_logger.level or logging.INFO, logging.INFO))
    return log_file


def install_excepthooks() -> None:
    """Install sys/thread exception hooks that write full tracebacks to logs."""
    logger = logging.getLogger(_LOGGER_NAME)

    def log_unhandled_exception(exc_type, exc_value, exc_traceback):
        logger.critical(
            "Unhandled exception in main thread",
            exc_info=(exc_type, exc_value, exc_traceback),
        )
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    def log_thread_exception(args: threading.ExceptHookArgs):
        if args.exc_value is None:
            logger.critical(
                "Unhandled exception in thread %s",
                args.thread.name if args.thread is not None else "<unknown>",
            )
            return
        logger.critical(
            "Unhandled exception in thread %s",
            args.thread.name if args.thread is not None else "<unknown>",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    sys.excepthook = log_unhandled_exception
    threading.excepthook = log_thread_exception


def run_with_crash_logging(context: str, func: Callable[..., T], *args, **kwargs) -> T:
    """Run a callable, logging context and traceback before re-raising failures."""
    try:
        return func(*args, **kwargs)
    except Exception:
        logging.getLogger(_LOGGER_NAME).exception("Unhandled exception during %s", context)
        raise
