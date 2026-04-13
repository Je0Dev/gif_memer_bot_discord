import logging
import logging.handlers
import os
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_dir: str = "logs") -> logging.Logger:
    log_level_value = getattr(logging, log_level.upper(), logging.INFO)

    Path(log_dir).mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level_value)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level_value)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, "bot.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level_value)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    error_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, "error.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    return root_logger
