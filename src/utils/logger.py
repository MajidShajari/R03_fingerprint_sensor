"""Logger configuration for the WhatsApp bot.
This module sets up a logger that writes logs to both a file and the console."""

# Standard Library
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import time

from src.config import settings


def setup_logger(name: str = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    Path(settings.LOGGER_PATH).mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        f"{settings.LOGGER_PATH}/{time.strftime('%Y_%m_%d')}.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
