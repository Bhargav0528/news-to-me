"""Edition assembly for the News To Me pipeline."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pipeline.generators.biztech import generate_biztech
from pipeline.generators.feature_sections import (
    generate_fun_section,
    generate_growth_section,
    generate_knowledge_section,
)
from pipeline.generators.news import generate_news_sections
from pipeline.generators.tldr import generate_tldr

DEFAULT_DB_PATH = Path('data/news_to_me.db')
OUTPUT_PATH = Path('data/edition.json')


class EditionAssembler:
    """Assemble the full edition JSON from stored pipeline artifacts."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)

    def assemble(self) -> dict[str, Any]:
        """Assemble and return the full edition payload."""
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            news_sections = generate_news_sections(connection)
            edition = {
                'date': datetime.now(timezone.utc).date().isoformat(),
                'edition_number': 1,
                'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                'pipeline_stats': {
                    'articles_fetched': connection.execute('SELECT COUNT(*) FROM raw_articles').fetchone()[0],
                    'full_text_success_rate': self._full_text_success_rate(connection),
                    'total_time_seconds': 0,
                    'token_usage': {},
                },
                'tldr': generate_tldr(news_sections),
                'news': news_sections,
                'biztech': generate_biztech(connection),
                'growth': generate_growth_section(),
                'knowledge': generate_knowledge_section(),
                'fun': generate_fun_section(),
            }
            return edition
        finally:
            connection.close()

    def write(self, output_path: str | Path = OUTPUT_PATH) -> Path:
        """Assemble and write the edition payload to disk."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(self.assemble(), indent=2))
        return output

    @staticmethod
    def _full_text_success_rate(connection: sqlite3.Connection) -> float:
        """Calculate the stored full-text success rate from the raw article table."""
        total = connection.execute('SELECT COUNT(*) FROM raw_articles').fetchone()[0]
        if total == 0:
            return 0.0
        success = connection.execute("SELECT COUNT(*) FROM raw_articles WHERE fetch_status = 'ok'").fetchone()[0]
        return success / total
