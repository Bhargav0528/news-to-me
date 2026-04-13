"""News section generation helpers for the News To Me pipeline."""

from __future__ import annotations

import sqlite3
from typing import Any


def _rows_to_articles(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    """Convert SQLite rows into structured news article summaries."""
    articles: list[dict[str, Any]] = []
    for row in rows:
        summary = (row['full_text'] or row['excerpt'] or '').strip()
        summary = ' '.join(summary.split())
        articles.append(
            {
                'headline': row['title'],
                'summary': summary[:900],
                'why_it_matters': f"This matters in {row['region']} because it is one of the stronger recent stories from {row['source']}.",
                'what_to_watch': 'Watch for follow-up reporting, policy response, and whether the story broadens beyond the initial update.',
                'public_reactions': 'Public reaction is still forming across early reporting and social discussion.',
                'context': f"Source: {row['source']}. Category: {row['category']}.",
                'source_url': row['url'],
            }
        )
    return articles


def generate_news_sections(connection: sqlite3.Connection) -> dict[str, list[dict[str, Any]]]:
    """Generate region-based news sections from stored raw articles."""
    sections = {
        'bangalore': ('bangalore', 5),
        'karnataka': ('karnataka', 5),
        'india': ('india', 5),
        'us': ('us', 5),
        'world': ('world', 5),
    }
    result: dict[str, list[dict[str, Any]]] = {}
    for key, (region, limit) in sections.items():
        rows = list(
            connection.execute(
                """
                SELECT title, url, source, category, region, excerpt, full_text, published_date
                FROM raw_articles
                WHERE region = ?
                ORDER BY COALESCE(published_date, '') DESC, full_text_length DESC
                LIMIT ?
                """,
                (region, limit),
            )
        )
        result[key] = _rows_to_articles(rows)
    return result
