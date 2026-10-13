"""Named logger config for library consumers that don't run the app."""
from __future__ import annotations

import logging

DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s :: %(message)s"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger