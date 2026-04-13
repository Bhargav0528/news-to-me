"""Config-driven RSS and Atom fetcher for the News To Me pipeline."""

from __future__ import annotations

import json
from collections import defaultdict
from itertools import zip_longest
from pathlib import Path
from typing import Any

import feedparser

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "rss_sources.json"


class RSSFetcher:
    """Fetch and normalize articles from configured RSS and Atom feeds."""

    def __init__(self, config_path: str | Path | None = None) -> None:
        self.config_path = Path(config_path) if config_path else CONFIG_PATH
        self.sources = self._load_sources()

    def _load_sources(self) -> list[dict[str, Any]]:
        """Load validated feed sources from configuration."""
        payload = json.loads(self.config_path.read_text())
        return payload["sources"]

    def fetch_source(self, source: dict[str, Any]) -> list[dict[str, Any]]:
        """Fetch and normalize entries for a single configured feed source."""
        feed = feedparser.parse(source["url"])
        if getattr(feed, "bozo", False) and not getattr(feed, "entries", []):
            raise RuntimeError(f"Failed to parse feed {source['name']}: {feed.bozo_exception}")

        articles: list[dict[str, Any]] = []
        for entry in feed.entries:
            title = (entry.get("title") or "").strip()
            link = (entry.get("link") or "").strip()
            if not title or not link:
                continue
            summary = entry.get("summary") or entry.get("description") or ""
            articles.append(
                {
                    "title": title,
                    "url": link,
                    "source": source["name"],
                    "category": source["section"],
                    "region": source["region"],
                    "published_date": entry.get("published") or entry.get("updated") or None,
                    "excerpt": self._clean_text(summary),
                }
            )
        return articles

    def fetch_all(self) -> list[dict[str, Any]]:
        """Fetch, then interleave, entries from all configured sources."""
        per_source_articles = [self.fetch_source(source) for source in self.sources]
        interleaved: list[dict[str, Any]] = []
        for group in zip_longest(*per_source_articles):
            for article in group:
                if article is not None:
                    interleaved.append(article)
        return interleaved

    def fetch_grouped(self) -> dict[str, list[dict[str, Any]]]:
        """Fetch articles grouped by region and category for balancing diagnostics."""
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for source in self.sources:
            articles = self.fetch_source(source)
            grouped[source['region']].extend(articles)
            grouped[source['section']].extend(articles)
        return dict(grouped)

    @staticmethod
    def _clean_text(value: str) -> str:
        """Normalize summary whitespace from feed payloads."""
        return " ".join(value.split())
