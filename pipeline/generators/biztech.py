"""Business and technology section generation helpers."""

from __future__ import annotations

import ast
import sqlite3
from typing import Any


def generate_biztech(connection: sqlite3.Connection) -> dict[str, Any]:
    """Generate market snapshot and business/tech article packets."""
    market_rows = list(
        connection.execute(
            "SELECT topic FROM topic_history WHERE section = ? ORDER BY id DESC LIMIT 4",
            ('market_snapshot',),
        )
    )
    indices = [ast.literal_eval(row['topic']) for row in reversed(market_rows)]
    article_rows = list(
        connection.execute(
            """
            SELECT title, url, source, category, excerpt, full_text
            FROM raw_articles
            WHERE category IN ('business', 'technology')
            ORDER BY full_text_length DESC, COALESCE(published_date, '') DESC
            LIMIT 5
            """
        )
    )
    articles = []
    for row in article_rows:
        text = ' '.join(((row['full_text'] or row['excerpt'] or '')).split())
        articles.append(
            {
                'headline': row['title'],
                'summary': text[:300],
                'market_impact': f"This may affect investor sentiment around {row['category']} trends.",
                'source_url': row['url'],
            }
        )
    return {
        'market_snapshot': {'indices': indices},
        'articles': articles,
    }
