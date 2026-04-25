"""Ingest stage of the News To Me pipeline.

Runs all RSS/API fetchers, full-text extraction, deduplication, and persistence to SQLite.
Fast (~2-5 min). Safe to run anywhere without exec timeout concerns.

Usage:
    python3 -m pipeline.ingest
    python3 -m pipeline.ingest --article-limit 50   # dev: limit to N articles
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from pipeline.fetchers.orchestrator import FetchOrchestrator
from pipeline.status import start, complete, fail

LOGGER = logging.getLogger(__name__)
DEFAULT_DB_PATH = Path("data/news_to_me.db")


def run(*, article_limit: int | None = None) -> dict[str, Any]:
    """Execute the ingest stage and return a summary dict.

    Writes pipeline_stats to the status file on success so that
    generate.py can verify an ingest ran before using its data.
    """
    load_dotenv()
    run_id = None

    try:
        # 1. Announce ingest start in the status file.
        run_id = __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat()
        start(stage="ingest", run_id=run_id)

        # 2. Run all fetchers.
        LOGGER.info("Starting ingest stage...")
        summary = FetchOrchestrator(
            DEFAULT_DB_PATH, article_limit=article_limit
        ).run()

        # 3. Record ingest completion in the status file.
        complete()

        LOGGER.info("Ingest complete: %s", summary)
        return summary

    except Exception as exc:
        LOGGER.exception("Ingest stage failed: %s", exc)
        fail(str(exc))
        raise


def main() -> None:
    """CLI entry point for the ingest stage."""
    parser = argparse.ArgumentParser(description="News To Me — ingest stage")
    parser.add_argument(
        "--article-limit",
        type=int,
        default=None,
        help="Limit total articles (dev/debug only)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable INFO logging"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    result = run(article_limit=args.article_limit)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
