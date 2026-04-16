"""Edition assembly for the News To Me pipeline."""

from __future__ import annotations

import ast
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pipeline.generators.engine import build_adapter, ModelConfig
from pipeline.generators.feature_sections import (
    generate_fun_section,
    generate_growth_section,
    generate_knowledge_section,
)
from pipeline.generators.news import generate_news_sections
from pipeline.generators.tldr import generate_tldr

DEFAULT_DB_PATH = Path('data/news_to_me.db')
OUTPUT_PATH = Path('data/edition.json')


def _prefetch_news_rows(db_path: Path) -> dict[str, list]:
    """Pre-fetch news rows from DB in the main thread."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = {}
    for region in ['bangalore', 'karnataka', 'india', 'us', 'world']:
        rows[region] = list(conn.execute(
            """
            SELECT title, url, source, category, region, excerpt, full_text, published_date
            FROM raw_articles
            WHERE region = ?
            ORDER BY COALESCE(published_date, '') DESC, full_text_length DESC
            LIMIT 5
            """, (region,)
        ))
    conn.close()
    return rows


def _prefetch_biztech_rows(db_path: Path) -> tuple[list, list]:
    """Pre-fetch biztech rows and market indices from DB in the main thread."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    biztech_rows = list(conn.execute(
        """
        SELECT title, url, source, category, excerpt, full_text
        FROM raw_articles
        WHERE category IN ('business', 'technology')
        ORDER BY full_text_length DESC, COALESCE(published_date, '') DESC
        LIMIT 5
        """
    ))
    market_rows = list(conn.execute(
        "SELECT topic FROM topic_history WHERE section = ? ORDER BY id DESC LIMIT 4",
        ('market_snapshot',)
    ))
    conn.close()
    indices = []
    for row in reversed(market_rows):
        try:
            indices.append(ast.literal_eval(row['topic']))
        except (ValueError, SyntaxError):
            # Fallback for malformed market data
            indices.append({'name': 'S&P 500', 'value': 0, 'change': 0, 'change_percent': 0})
    return biztech_rows, indices


class EditionAssembler:
    """Assemble the full edition JSON from stored pipeline artifacts."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH, adapter=None) -> None:
        self.db_path = Path(db_path)
        self.adapter = adapter or build_adapter(ModelConfig())

    def assemble(self) -> dict[str, Any]:
        """Assemble and return the full edition payload."""
        # Pre-fetch all DB data in main thread (avoids SQLite thread issues)
        news_rows = _prefetch_news_rows(self.db_path)
        biztech_rows, indices = _prefetch_biztech_rows(self.db_path)
        
        news_sections = generate_news_sections(news_rows, adapter=self.adapter)
        
        from pipeline.generators.biztech import generate_biztech
        
        edition = {
            'date': datetime.now(timezone.utc).date().isoformat(),
            'edition_number': 1,
            'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            'pipeline_stats': {
                'articles_fetched': self._count_articles(),
                'full_text_success_rate': self._full_text_success_rate(),
                'total_time_seconds': 0,
                'token_usage': {},
            },
            'tldr': generate_tldr(news_sections, adapter=self.adapter),
            'news': news_sections,
            'biztech': generate_biztech(biztech_rows, indices, adapter=self.adapter),
            'growth': generate_growth_section(adapter=self.adapter),
            'knowledge': generate_knowledge_section(adapter=self.adapter),
            'fun': generate_fun_section(adapter=self.adapter),
        }
        return edition

    def write(self, output_path: str | Path = OUTPUT_PATH) -> Path:
        """Assemble and write the edition payload to disk."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(self.assemble(), indent=2))
        return output

    def _count_articles(self) -> int:
        """Count total raw articles."""
        conn = sqlite3.connect(self.db_path)
        count = conn.execute('SELECT COUNT(*) FROM raw_articles').fetchone()[0]
        conn.close()
        return count

    def _full_text_success_rate(self) -> float:
        """Calculate the stored full-text success rate from the raw article table."""
        conn = sqlite3.connect(self.db_path)
        total = conn.execute('SELECT COUNT(*) FROM raw_articles').fetchone()[0]
        if total == 0:
            conn.close()
            return 0.0
        success = conn.execute("SELECT COUNT(*) FROM raw_articles WHERE fetch_status = 'ok'").fetchone()[0]
        conn.close()
        return success / total