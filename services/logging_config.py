import logging
import os

__all__ = ["setup_logging"]

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

def setup_logging():
    root = logging.getLogger()
    if root.handlers:
        return

    level = getattr(logging, LOG_LEVEL, logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    ))

    root.setLevel(level)
    root.addHandler(handler)

    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
