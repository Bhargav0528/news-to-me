PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS ingestion_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT NOT NULL,
  source_count INTEGER NOT NULL DEFAULT 0,
  fetched_count INTEGER NOT NULL DEFAULT 0,
  inserted_count INTEGER NOT NULL DEFAULT 0,
  duplicate_count INTEGER NOT NULL DEFAULT 0,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  region TEXT NOT NULL,
  section TEXT NOT NULL,
  tier TEXT NOT NULL,
  url TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS articles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dedupe_key TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  source_id TEXT NOT NULL,
  source_name TEXT,
  section TEXT NOT NULL,
  region TEXT NOT NULL,
  published_at TEXT,
  excerpt TEXT,
  content TEXT,
  author TEXT,
  language TEXT,
  inserted_at TEXT NOT NULL,
  last_seen_run_id INTEGER,
  FOREIGN KEY (source_id) REFERENCES sources(id),
  FOREIGN KEY (last_seen_run_id) REFERENCES ingestion_runs(id)
);

CREATE INDEX IF NOT EXISTS idx_articles_section_region ON articles(section, region);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_source_id ON articles(source_id);
