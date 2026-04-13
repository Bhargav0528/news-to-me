"""End-to-end fetch orchestration for the News To Me pipeline."""

from __future__ import annotations

import logging
from collections import Counter
from pathlib import Path
from time import perf_counter
from typing import Any

from pipeline.db import get_connection, init_db
from pipeline.fetchers.article_fetcher import ArticleFetcher
from pipeline.fetchers.dedup import deduplicate_articles
from pipeline.fetchers.rss_fetcher import RSSFetcher
from pipeline.fetchers.stock_fetcher import StockFetcher

LOGGER = logging.getLogger(__name__)
DEFAULT_DB_PATH = Path("data/news_to_me.db")


class FetchOrchestrator:
    """Run feed ingestion, full-text extraction, deduplication, and persistence."""

    def __init__(
        self,
        db_path: str | Path = DEFAULT_DB_PATH,
        article_limit: int | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.article_limit = article_limit
        self.rss_fetcher = RSSFetcher()
        self.article_fetcher = ArticleFetcher(delay_seconds=0)
        self.stock_fetcher = StockFetcher()

    def run(self) -> dict[str, Any]:
        """Execute the full ingestion pipeline and return summary stats."""
        start_time = perf_counter()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = init_db(self.db_path)
        try:
            raw_articles = self.rss_fetcher.fetch_all()
            if self.article_limit is not None:
                raw_articles = raw_articles[: self.article_limit]
            enriched_articles = self.article_fetcher.enrich_records(raw_articles)
            deduped_articles, duplicates_removed = deduplicate_articles(enriched_articles)
            inserted_count = self._store_articles(connection, deduped_articles)
            market_snapshot = self.stock_fetcher.fetch_snapshot()
            self._store_market_snapshot(connection, market_snapshot)

            full_text_successes = sum(1 for article in enriched_articles if article.get("fetch_status") == "ok")
            region_counts = Counter(article.get("region", "unknown") for article in deduped_articles)
            category_counts = Counter(article.get("category", "unknown") for article in deduped_articles)
            summary = {
                "articles_fetched": len(raw_articles),
                "articles_after_dedup": len(deduped_articles),
                "articles_inserted": inserted_count,
                "duplicates_removed": duplicates_removed,
                "full_text_success_rate": full_text_successes / len(enriched_articles) if enriched_articles else 0.0,
                "articles_per_region": dict(region_counts),
                "articles_per_category": dict(category_counts),
                "market_indices": len(market_snapshot["indices"]),
                "total_time_seconds": round(perf_counter() - start_time, 2),
            }
            LOGGER.info("Fetch summary: %s", summary)
            return summary
        finally:
            connection.close()

    def _store_articles(self, connection, articles: list[dict[str, Any]]) -> int:
        """Insert deduplicated article records into SQLite."""
        inserted = 0
        for article in articles:
            connection.execute(
                """
                INSERT OR REPLACE INTO raw_articles (
                    title, url, source, category, region, excerpt, full_text,
                    full_text_length, fetch_status, fetch_method, fetch_error, published_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    article.get("title"),
                    article.get("url"),
                    article.get("source"),
                    article.get("category"),
                    article.get("region"),
                    article.get("excerpt"),
                    article.get("full_text"),
                    article.get("full_text_length", 0),
                    article.get("fetch_status"),
                    article.get("fetch_method"),
                    article.get("fetch_error"),
                    article.get("published_date"),
                ),
            )
            inserted += 1
        connection.commit()
        return inserted

    def _store_market_snapshot(self, connection, snapshot: dict[str, Any]) -> None:
        """Persist market snapshot into topic history as a lightweight placeholder store."""
        for index in snapshot["indices"]:
            connection.execute(
                "INSERT INTO topic_history (date, section, topic) VALUES (date('now'), ?, ?)",
                ("market_snapshot", str(index)),
            )
        connection.commit()


def main() -> None:
    """CLI entry point for the fetch orchestrator."""
    logging.basicConfig(level=logging.INFO)
    summary = FetchOrchestrator().run()
    print(summary)


if __name__ == "__main__":
    main()
