"""Logger configuration for the WhatsApp bot.
This module sets up a logger that writes logs to both a file and the console."""

import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.config import LOGGER_PATH


def setup_logger(name: str = None) -> logging.Logger:
    local_logger = logging.getLogger(name)
    local_logger.setLevel(logging.INFO)
    if local_logger.handlers:
        return local_logger
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(processName)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if not Path(LOGGER_PATH).exists():
        Path(LOGGER_PATH).mkdir()
    file_handler = RotatingFileHandler(
        f"{LOGGER_PATH}/{time.strftime('%Y_%m_%d')}.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    local_logger.addHandler(file_handler)
    return local_logger
