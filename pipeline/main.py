"""Entry point for the News To Me production pipeline."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from pipeline.fetchers.orchestrator import FetchOrchestrator
from pipeline.generators.assembler import EditionAssembler
from pipeline.publishers.deployer import Deployer
from pipeline.publishers.emailer import EmailPublisher

def _commit_edition_json(git_dir: Path, edition: dict[str, Any]) -> str | None:
    """Commit edition.json to git and push.

    Writes to both data/edition.json and web/public/data/edition.json,
    then commits and pushes to origin/main. This ensures the deployed
    site always has the latest content even if deploy fails.
    """
    import subprocess, os, time
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "News To Me Pipeline"
    env["GIT_AUTHOR_EMAIL"] = "pipeline@newstome.local"
    env["GIT_COMMITTER_NAME"] = env["GIT_AUTHOR_NAME"]
    env["GIT_COMMITTER_EMAIL"] = env["GIT_AUTHOR_EMAIL"]

    try:
        result = subprocess.run(
            ["git", "add", "data/edition.json", "web/public/data/edition.json"],
            cwd=git_dir, capture_output=True, text=True,
        )
        diff = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            cwd=git_dir, capture_output=True, text=True,
        )
        if not diff.stdout.strip():
            LOGGER.info("edition.json unchanged — no git commit needed")
            return None
        message = f"docs: update edition.json to {edition.get('date', 'unknown')} [skip ci]"
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=git_dir, check=True, env=env,
        )
        hash_ = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=git_dir, capture_output=True, text=True,
        ).stdout.strip()
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=git_dir, capture_output=True, text=True,
        )
        LOGGER.info("Edition JSON committed: %s", hash_)
        return hash_
    except subprocess.CalledProcessError as exc:
        LOGGER.warning("Git commit failed (non-fatal): %s", exc)
        return None

LOGGER = logging.getLogger(__name__)
DEFAULT_DB_PATH = Path('data/news_to_me.db')
DEFAULT_EDITION_PATH = Path('data/edition.json')
DEFAULT_EMAIL_PREVIEW_PATH = Path('data/email_preview.json')
WEB_EDITION_PATH = Path('web/public/data/edition.json')


def run(*, article_limit: int | None = None, send_email: bool = False, deploy: bool = False) -> dict[str, Any]:
    """Run ingestion, assemble the edition, and optionally send the email or deploy."""
    load_dotenv()
    fetch_summary = FetchOrchestrator(DEFAULT_DB_PATH, article_limit=article_limit).run()
    assembler = EditionAssembler(DEFAULT_DB_PATH)
    edition = assembler.assemble()
    DEFAULT_EDITION_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_EDITION_PATH.write_text(json.dumps(edition, indent=2))
    WEB_EDITION_PATH.parent.mkdir(parents=True, exist_ok=True)
    WEB_EDITION_PATH.write_text(json.dumps(edition, indent=2))

    publisher = EmailPublisher()
    preview_path = publisher.write_preview(edition, DEFAULT_EMAIL_PREVIEW_PATH)

    # Commit to git BEFORE deploy — ensures website gets fresh content
    # even if deploy step fails. Vercel deploys on next push.
    commit_hash = _commit_edition_json(Path(__file__).resolve().parents[1], edition)

    deployed_url: str | None = None
    if deploy:
        LOGGER.info('Triggering Vercel deploy...')
        deployed_url = Deployer().deploy()
        LOGGER.info('Deployed to: %s', deployed_url)

    if send_email:
        if deployed_url:
            edition['_live_url'] = deployed_url
        publisher.send(edition)

    result = {
        'fetch_summary': fetch_summary,
        'edition_path': str(DEFAULT_EDITION_PATH),
        'email_preview_path': str(preview_path),
        'email_sent': send_email,
        'deployed_url': deployed_url,
        'commit_hash': commit_hash,
    }
    LOGGER.info('Pipeline result: %s', result)
    return result


def main() -> None:
    """CLI entry point for the full News To Me pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--article-limit', type=int, default=None)
    parser.add_argument('--send-email', action='store_true')
    parser.add_argument('--deploy', action='store_true', help='Deploy to Vercel after assembling edition')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    result = run(article_limit=args.article_limit, send_email=args.send_email, deploy=args.deploy)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
