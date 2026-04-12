#!/usr/bin/env python3
import datetime as dt
import hashlib
import html
import json
import pathlib
import sqlite3
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BASE_DIR = pathlib.Path(__file__).resolve().parent
REGISTRY_PATH = BASE_DIR / "source_registry.json"
SCHEMA_PATH = BASE_DIR / "schema.sql"
OUTPUT_DIR = BASE_DIR / "sample_output"
DB_PATH = OUTPUT_DIR / "news_to_me.db"
SUMMARY_PATH = OUTPUT_DIR / "run_summary.json"
USER_AGENT = "news-to-me-scrum-2-spike/0.1"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def canonicalize_url(value: str) -> str:
    if not value:
        return ""
    parsed = urllib.parse.urlsplit(value.strip())
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    filtered = [(k, v) for k, v in query if not k.lower().startswith("utm_")]
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc.lower(), parsed.path, urllib.parse.urlencode(filtered), ""))


def normalize_text(value: str) -> str:
    return " ".join((value or "").split()).strip()


def dedupe_key(url: str, title: str) -> str:
    basis = canonicalize_url(url) or normalize_text(title).lower()
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def text_or_empty(node, path):
    child = node.find(path)
    if child is None or child.text is None:
        return ""
    return normalize_text(html.unescape(child.text))


def load_registry():
    with REGISTRY_PATH.open() as fh:
        return json.load(fh)["sources"]


def init_db(conn: sqlite3.Connection):
    conn.executescript(SCHEMA_PATH.read_text())
    conn.commit()


def upsert_sources(conn: sqlite3.Connection, sources):
    conn.executemany(
        """
        INSERT INTO sources (id, kind, region, section, tier, url, active)
        VALUES (:id, :kind, :region, :section, :tier, :url, 1)
        ON CONFLICT(id) DO UPDATE SET
          kind=excluded.kind,
          region=excluded.region,
          section=excluded.section,
          tier=excluded.tier,
          url=excluded.url,
          active=1
        """,
        sources,
    )
    conn.commit()


def create_run(conn: sqlite3.Connection, source_count: int) -> int:
    cur = conn.execute(
        "INSERT INTO ingestion_runs (started_at, status, source_count) VALUES (?, ?, ?)",
        (now_iso(), "running", source_count),
    )
    conn.commit()
    return int(cur.lastrowid)


def finish_run(conn: sqlite3.Connection, run_id: int, fetched: int, inserted: int, duplicates: int, notes: str = ""):
    conn.execute(
        """
        UPDATE ingestion_runs
        SET finished_at = ?, status = ?, fetched_count = ?, inserted_count = ?, duplicate_count = ?, notes = ?
        WHERE id = ?
        """,
        (now_iso(), "completed", fetched, inserted, duplicates, notes, run_id),
    )
    conn.commit()


def fetch_url(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.1"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def parse_rss(xml_bytes: bytes):
    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    items = channel.findall("item") if channel is not None else []
    entries = []
    for item in items:
        title = text_or_empty(item, "title")
        link = text_or_empty(item, "link")
        if not title or not link:
            continue
        entries.append(
            {
                "title": title,
                "url": link,
                "published_at": text_or_empty(item, "pubDate"),
                "excerpt": text_or_empty(item, "description"),
                "author": text_or_empty(item, "author") or text_or_empty(item, "creator"),
                "source_name": "",
                "language": "en",
            }
        )
    return entries


def insert_article(conn: sqlite3.Connection, run_id: int, source: dict, article: dict) -> bool:
    key = dedupe_key(article["url"], article["title"])
    cur = conn.execute(
        """
        INSERT OR IGNORE INTO articles (
          dedupe_key, title, url, source_id, source_name, section, region,
          published_at, excerpt, content, author, language, inserted_at, last_seen_run_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            key,
            article["title"],
            article["url"],
            source["id"],
            article.get("source_name") or source["id"],
            source["section"],
            source["region"],
            article.get("published_at", ""),
            article.get("excerpt", ""),
            article.get("content", ""),
            article.get("author", ""),
            article.get("language", "en"),
            now_iso(),
            run_id,
        ),
    )
    if cur.rowcount == 0:
        conn.execute("UPDATE articles SET last_seen_run_id = ? WHERE dedupe_key = ?", (run_id, key))
        return False
    return True


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = load_registry()
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    upsert_sources(conn, sources)
    run_id = create_run(conn, len(sources))

    fetched = 0
    inserted = 0
    duplicates = 0
    source_summaries = []

    for source in sources:
        try:
            payload = fetch_url(source["url"])
            articles = parse_rss(payload)
            fetched += len(articles)
            inserted_here = 0
            duplicate_here = 0
            for article in articles:
                if insert_article(conn, run_id, source, article):
                    inserted += 1
                    inserted_here += 1
                else:
                    duplicates += 1
                    duplicate_here += 1
            source_summaries.append({
                "source_id": source["id"],
                "fetched": len(articles),
                "inserted": inserted_here,
                "duplicates": duplicate_here,
                "status": "ok",
            })
            conn.commit()
        except Exception as exc:
            source_summaries.append({
                "source_id": source["id"],
                "fetched": 0,
                "inserted": 0,
                "duplicates": 0,
                "status": "error",
                "error": str(exc),
            })

    finish_run(conn, run_id, fetched, inserted, duplicates, notes="SCRUM-2 foundation spike run")
    article_count = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    summary = {
        "run_id": run_id,
        "db_path": str(DB_PATH),
        "source_count": len(sources),
        "fetched_count": fetched,
        "inserted_count": inserted,
        "duplicate_count": duplicates,
        "stored_article_count": article_count,
        "sources": source_summaries,
        "completed_at": now_iso(),
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
