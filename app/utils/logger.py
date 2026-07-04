"""
Centralized logging configuration using loguru.

Every module in this project should import `logger` from here instead of
using `print()` or configuring its own logger. This guarantees consistent
formatting, log levels, and file output across the entire application.
"""

import sys
from pathlib import Path
from loguru import logger

from config.settings import settings

def configure_logger() -> None:
    """
    Configure loguru sinks: colored console output for development,
    and a rotating file sink for persistent logs.

    Called once at application startup (see app/main.py).
    """
    logs_dir = Path(settings.logs_directory)
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()  # remove default handler to avoid duplicate logs

    # Console sink — human-readable, colorized
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
            "- <level>{message}</level>"
        ),
        colorize=True,
    )

    # File sink — rotates at 10MB, retains 7 days, useful for debugging deployments
    logger.add(
        logs_dir / "app.log",
        level=settings.log_level,
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}:{function}:{line} - {message}",
    )


# Export a ready-to-use logger instance
__all__ = ["logger", "configure_logger"]