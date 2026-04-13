"""Entry point for the News To Me production pipeline."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

from pipeline.fetchers.orchestrator import FetchOrchestrator
from pipeline.generators.assembler import EditionAssembler
from pipeline.publishers.emailer import EmailPublisher

LOGGER = logging.getLogger(__name__)
DEFAULT_DB_PATH = Path('data/news_to_me.db')
DEFAULT_EDITION_PATH = Path('data/edition.json')
DEFAULT_EMAIL_PREVIEW_PATH = Path('data/email_preview.json')


def run(*, article_limit: int | None = None, send_email: bool = False) -> dict[str, Any]:
    """Run ingestion, assemble the edition, and optionally send the email."""
    fetch_summary = FetchOrchestrator(DEFAULT_DB_PATH, article_limit=article_limit).run()
    assembler = EditionAssembler(DEFAULT_DB_PATH)
    edition = assembler.assemble()
    DEFAULT_EDITION_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_EDITION_PATH.write_text(json.dumps(edition, indent=2))

    publisher = EmailPublisher()
    preview_path = publisher.write_preview(edition, DEFAULT_EMAIL_PREVIEW_PATH)
    if send_email:
        publisher.send(edition)

    result = {
        'fetch_summary': fetch_summary,
        'edition_path': str(DEFAULT_EDITION_PATH),
        'email_preview_path': str(preview_path),
        'email_sent': send_email,
    }
    LOGGER.info('Pipeline result: %s', result)
    return result


def main() -> None:
    """CLI entry point for the full News To Me pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--article-limit', type=int, default=None)
    parser.add_argument('--send-email', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    result = run(article_limit=args.article_limit, send_email=args.send_email)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
