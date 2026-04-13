"""Entry point for the News To Me production pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

from pipeline.db import ensure_db

LOGGER = logging.getLogger(__name__)
DEFAULT_DB_PATH = Path("data/news_to_me.db")


def run() -> Path:
    """Initialize core pipeline state and return the database path."""
    db_path = ensure_db(DEFAULT_DB_PATH)
    LOGGER.info("Initialized pipeline database at %s", db_path)
    return db_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
