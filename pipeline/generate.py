"""Generate stage of the News To Me pipeline.

Reads the most recent ingest data from SQLite, runs all LLM section generators
(TLDR → news regions → biztech → growth → knowledge → fun), assembles edition.json,
then triggers git commit and email on success only.

Slow (~10-15 min) — but runs alone in its own process budget.

Usage:
    python3 -m pipeline.generate
    python3 -m pipeline.generate --deploy   # also deploy to Vercel
    python3 -m pipeline.generate --no-email # skip email (dev/debug)
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from pipeline.db import get_connection
from pipeline.generators.assembler import EditionAssembler
from pipeline.generators.engine import build_adapter, ModelConfig
from pipeline.generators.feature_sections import (
    generate_fun_section,
    generate_growth_section,
    generate_knowledge_section,
)
from pipeline.generators.news import generate_news_region
from pipeline.generators.tldr import generate_tldr
from pipeline.publishers.deployer import Deployer
from pipeline.publishers.emailer import EmailPublisher
from pipeline.status import start, set_step, complete, fail, get_status, GENERATE_STEPS

LOGGER = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path("data/news_to_me.db")
DEFAULT_EDITION_PATH = Path("data/edition.json")
DEFAULT_EMAIL_PREVIEW_PATH = Path("data/email_preview.json")
WEB_EDITION_PATH = Path("web/public/data/edition.json")


def _check_ingest_ran(db_path: Path) -> None:
    """Verify that the DB contains articles from a prior ingest run.

    Raises RuntimeError if the DB is empty, has no tables, or contains zero articles —
    this means python3 -m pipeline.ingest needs to run first.
    """
    import sqlite3
    # If DB doesn't exist yet, get_connection creates an empty file — detect that.
    if not db_path.exists():
        raise RuntimeError(
            f"Database not found at {db_path}. Run `python3 -m pipeline.ingest` first."
        )
    conn = sqlite3.connect(db_path)
    try:
        # Check that the raw_articles table exists.
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='raw_articles'"
        ).fetchone()
        if not tables:
            raise RuntimeError(
                f"Database at {db_path} has no raw_articles table. "
                "Run `python3 -m pipeline.ingest` first."
            )
        count = conn.execute("SELECT COUNT(*) FROM raw_articles").fetchone()[0]
        if count == 0:
            raise RuntimeError(
                "Database has 0 articles. Run `python3 -m pipeline.ingest` first."
            )
    finally:
        conn.close()


def _assemble_with_tracking(
    db_path: Path,
    adapter,
) -> dict[str, Any]:
    """Assemble edition with status tracking before each LLM section.

    Calls status.set_step() at the start of each section so the status file
    always shows exactly where the pipeline is or where it died.
    """
    from pipeline.generators.biztech import generate_biztech
    from pipeline.generators.assembler import _prefetch_biztech_rows, _prefetch_news_rows

    # --- TLDR ----------------------------------------------------------
    set_step("tldr")
    news_rows = _prefetch_news_rows(db_path)
    tldr = generate_tldr(news_rows, adapter=adapter)

    # --- News sections (one step per region) ----------------------------
    # Each region is a separate LLM call so the status file accurately
    # reflects which region is currently being generated.
    news_sections = {}
    for region in ["bangalore", "karnataka", "india", "us", "world"]:
        set_step(f"news_{region}")
        news_sections[region] = generate_news_region(
            news_rows.get(region, []),
            region=region,
            adapter=adapter,
        )

    # --- Biz/Tech ------------------------------------------------------
    set_step("biztech")
    biztech_rows, indices = _prefetch_biztech_rows(db_path)
    biztech = generate_biztech(biztech_rows, indices, adapter=adapter)

    # --- Growth --------------------------------------------------------
    set_step("growth")
    growth = generate_growth_section(adapter=adapter)

    # --- Knowledge ------------------------------------------------------
    set_step("knowledge")
    knowledge = generate_knowledge_section(adapter=adapter)

    # --- Fun -----------------------------------------------------------
    set_step("fun")
    fun = generate_fun_section(adapter=adapter)

    return {
        "tldr": tldr,
        "news": news_sections,
        "biztech": biztech,
        "growth": growth,
        "knowledge": knowledge,
        "fun": fun,
    }


def _commit_edition_json(edition: dict[str, Any]) -> str | None:
    """Commit edition.json to git and push.

    Returns the git commit hash on success, or None on failure.
    Does NOT run if there are no changes.
    """
    import subprocess
    try:
        result = subprocess.run(
            ["git", "add", "data/edition.json", "web/public/data/edition.json"],
            capture_output=True,
            text=True,
        )
        diff = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            capture_output=True,
            text=True,
        )
        if not diff.stdout.strip():
            LOGGER.info("No changes to commit for edition.json")
            return None
        subprocess.run(
            ["git", "commit", "-m", f"docs: update edition.json to {edition.get('date', 'unknown')} [skip ci]"],
            capture_output=True,
            text=True,
        )
        hash_ = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
        ).stdout.strip()
        subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
        LOGGER.info("Edition JSON committed: %s", hash_)
        return hash_
    except Exception as exc:
        LOGGER.warning("Git commit failed (non-fatal): %s", exc)
        return None


def run(
    *,
    db_path: Path = DEFAULT_DB_PATH,
    deploy: bool = False,
    send_email: bool = True,
) -> dict[str, Any]:
    """Execute the generate stage and return a result dict.

    On success: writes edition.json, triggers git commit, triggers email
    (if send_email=True), and marks status as completed.

    On failure: marks status as failed and re-raises.
    """
    load_dotenv()
    run_id = datetime.now(timezone.utc).isoformat()

    try:
        # Announce generate start.
        start(stage="generate", steps=GENERATE_STEPS, run_id=run_id)

        # Verify ingest ran first (raises if DB is empty).
        _check_ingest_ran(db_path)

        # Run all LLM generators with per-section status tracking.
        adapter = build_adapter(ModelConfig())
        sections = _assemble_with_tracking(db_path, adapter)

        # Assemble the final edition payload.
        edition: dict[str, Any] = {
            "date": datetime.now(timezone.utc).date().isoformat(),
            "edition_number": 1,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "pipeline_stats": {
                "articles_fetched": _count_articles(db_path),
                "full_text_success_rate": _full_text_rate(db_path),
                "total_time_seconds": 0,
                "token_usage": {},
            },
            **sections,
        }

        # Write edition.json to both data/ and web/public/data/.
        DEFAULT_EDITION_PATH.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_EDITION_PATH.write_text(json.dumps(edition, indent=2))
        WEB_EDITION_PATH.parent.mkdir(parents=True, exist_ok=True)
        WEB_EDITION_PATH.write_text(json.dumps(edition, indent=2))
        LOGGER.info("edition.json written to %s and %s", DEFAULT_EDITION_PATH, WEB_EDITION_PATH)

        # Commit to git (only on success).
        commit_hash = _commit_edition_json(edition)

        # Deploy to Vercel if requested (before email — email needs the URL).
        deployed_url: str | None = None
        if deploy:
            LOGGER.info("Triggering Vercel deploy...")
            deployed_url = Deployer().deploy()
            LOGGER.info("Deployed to: %s", deployed_url)
            edition["_live_url"] = deployed_url
            # Re-write with the URL embedded.
            DEFAULT_EDITION_PATH.write_text(json.dumps(edition, indent=2))
            WEB_EDITION_PATH.write_text(json.dumps(edition, indent=2))

        # Write email preview.
        publisher = EmailPublisher()
        preview_path = publisher.write_preview(edition, DEFAULT_EMAIL_PREVIEW_PATH)

        # Send email — ONLY on full success.
        email_sent = False
        if send_email:
            publisher.send(edition)
            email_sent = True
            LOGGER.info("Email sent.")

        # Mark pipeline as completed.
        complete()

        result = {
            "edition_path": str(DEFAULT_EDITION_PATH),
            "email_preview_path": str(preview_path),
            "email_sent": email_sent,
            "deployed_url": deployed_url,
            "commit_hash": commit_hash,
        }
        LOGGER.info("Generate stage complete: %s", result)
        return result

    except Exception as exc:
        LOGGER.exception("Generate stage failed: %s", exc)
        fail(str(exc))
        raise


def _count_articles(db_path: Path) -> int:
    conn = get_connection(db_path)
    count = conn.execute("SELECT COUNT(*) FROM raw_articles").fetchone()[0]
    conn.close()
    return count


def _full_text_rate(db_path: Path) -> float:
    conn = get_connection(db_path)
    total = conn.execute("SELECT COUNT(*) FROM raw_articles").fetchone()[0]
    if total == 0:
        conn.close()
        return 0.0
    success = conn.execute(
        "SELECT COUNT(*) FROM raw_articles WHERE fetch_status = 'ok'"
    ).fetchone()[0]
    conn.close()
    return success / total


def main() -> None:
    """CLI entry point for the generate stage."""
    parser = argparse.ArgumentParser(description="News To Me — generate stage")
    parser.add_argument(
        "--deploy", action="store_true", help="Deploy to Vercel after assembling"
    )
    parser.add_argument(
        "--no-email", action="store_true", help="Skip sending email (dev/debug)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable DEBUG logging"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    result = run(deploy=args.deploy, send_email=not args.no_email)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
