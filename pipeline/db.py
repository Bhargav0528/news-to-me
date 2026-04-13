"""SQLite helpers for the News To Me production pipeline."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS raw_articles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  url TEXT UNIQUE,
  source TEXT,
  category TEXT,
  region TEXT,
  excerpt TEXT,
  full_text TEXT,
  full_text_length INTEGER DEFAULT 0,
  fetch_status TEXT DEFAULT 'pending',
  fetch_method TEXT,
  fetch_error TEXT,
  published_date TEXT,
  fetch_date TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS editions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT UNIQUE NOT NULL,
  edition_number INTEGER,
  edition_json TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS puzzle_answers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL,
  puzzle_type TEXT NOT NULL,
  answer_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS topic_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL,
  section TEXT NOT NULL,
  topic TEXT NOT NULL
);
"""


def get_connection(db_path: str | Path) -> sqlite3.Connection:
    """Create a SQLite connection for the pipeline database."""
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path: str | Path) -> sqlite3.Connection:
    """Initialize the pipeline database schema and return an open connection."""
    connection = get_connection(db_path)
    connection.executescript(SCHEMA_SQL)
    connection.commit()
    return connection


def ensure_db(db_path: str | Path) -> Path:
    """Create the database file and schema if needed, then return its path."""
    resolved_path = Path(db_path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    connection: Optional[sqlite3.Connection] = None
    try:
        connection = init_db(resolved_path)
    finally:
        if connection is not None:
            connection.close()
    return resolved_path
