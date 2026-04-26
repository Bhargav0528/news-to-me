"""Generate stage of the News To Me pipeline.

Reads the most recent ingest data from SQLite, runs all LLM section generators
(TLDR → news regions → biztech → growth → knowledge → fun), assembles edition.json,
then deploys, waits for rebuild, and sends email — only on full success.

The email-last ordering is intentional: the reader should never click through
from an email to find stale site content.

Usage:
    python3 -m pipeline.generate
    python3 -m pipeline.generate --deploy   # also deploy to Vercel
    python3 -m pipeline.generate --no-email # skip email (dev/debug)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import time
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
from pipeline.utils.validation import validate_and_log

LOGGER = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path("data/news_to_me.db")
DEFAULT_EDITION_PATH = Path("data/edition.json")
DEFAULT_EMAIL_PREVIEW_PATH = Path("data/email_preview.json")
WEB_EDITION_PATH = Path("web/public/data/edition.json")
POST_DEPLOY_WAIT_SECONDS = 120  # 2 minutes for Vercel rebuild
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "bhargavbangalorevmurthy@gmail.com")


def _build_version_hash(edition: dict[str, Any]) -> str:
    """Generate a short version hash from the edition content.

    Used to detect mismatch between what the email claims and what's on the site.
    """
    payload = json.dumps(
        {"date": edition.get("date"), "generated_at": edition.get("generated_at")},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:8]


def _check_ingest_ran(db_path: Path) -> None:
    """Verify that the DB contains articles from a prior ingest run.

    Raises RuntimeError if the DB is empty, has no tables, or contains zero articles.
    """
    import sqlite3

    if not db_path.exists():
        raise RuntimeError(
            f"Database not found at {db_path}. Run `python3 -m pipeline.ingest` first."
        )
    conn = sqlite3.connect(db_path)
    try:
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


def _alert_admin(reason: str, edition: dict[str, Any] | None = None) -> None:
    """Send an admin alert email for catastrophic pipeline failures."""
    try:
        publisher = EmailPublisher()
        from pipeline.publishers.emailer import EmailConfig

        alert_config = EmailConfig(
            recipient=ADMIN_EMAIL,
            edition_url="https://web-sand-two-88.vercel.app",
        )
        alert_publisher = EmailPublisher(config=alert_config)

        subject = f"[ALERT] News To Me pipeline failed: {reason}"
        text = (
            f"Pipeline aborted on {datetime.now(timezone.utc).date().isoformat()}.\n"
            f"Reason: {reason}\n"
            f"Check data/broken_editions/ for details.\n"
            f"Edition: {edition.get('date', 'unknown') if edition else 'N/A'}"
        )
        # Use raw AgentMail client for admin alert (no AgentMail object needed — use send directly)
        from agentmail import AgentMail

        client = AgentMail(api_key=os.getenv("AGENTMAIL_API_KEY", ""))
        client.inboxes.messages.send(
            inbox_id=alert_config.inbox_id,
            to=ADMIN_EMAIL,
            subject=subject,
            text=text,
        )
        LOGGER.info("Admin alert sent to %s", ADMIN_EMAIL)
    except Exception as exc:
        LOGGER.error("Failed to send admin alert: %s", exc)


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


def run(
    *,
    db_path: Path = DEFAULT_DB_PATH,
    deploy: bool = False,
    send_email: bool = True,
) -> dict[str, Any]:
    """Execute the generate stage and return a result dict.

    Ordering (email-last):
      1. Validate DB has data
      2. Run all LLM generators
      3. Validate edition schema
      4. Write edition.json
      5. Deploy to Vercel (if --deploy)
      6. Wait 2 min for Vercel rebuild
      7. Send email ONLY if all above succeeded

    On failure: marks status as failed, logs broken edition, alerts admin, re-raises.
    """
    load_dotenv()
    run_id = datetime.now(timezone.utc).isoformat()
    stage_failed = False
    failure_reason = ""

    try:
        start(stage="generate", steps=GENERATE_STEPS, run_id=run_id)
        _check_ingest_ran(db_path)

        adapter = build_adapter(ModelConfig())
        sections = _run_all_sections(db_path, adapter)
        edition = _build_edition(db_path, sections)
        version_hash = _build_version_hash(edition)
        edition["_version_hash"] = version_hash

        # Validate before writing
        if not validate_and_log(edition, DEFAULT_EDITION_PATH.parent):
            broken_path = DEFAULT_EDITION_PATH.parent / "broken_editions"
            raise RuntimeError(
                f"Edition validation failed. Broken edition written to {broken_path}. "
                "Fix pipeline and re-run. Email not sent."
            )

        # Write edition.json
        _write_edition(edition)
        LOGGER.info("edition.json written")

        # Deploy if requested
        deployed_url: str | None = None
        if deploy:
            deployed_url = Deployer().deploy()
            LOGGER.info("Deployed to: %s", deployed_url)
            # Re-write with the URL embedded after deploy
            edition["_live_url"] = deployed_url
            _write_edition(edition)

            # Wait for Vercel rebuild (~2 min)
            LOGGER.info("Waiting %ds for Vercel rebuild...", POST_DEPLOY_WAIT_SECONDS)
            time.sleep(POST_DEPLOY_WAIT_SECONDS)

        # Send email — ONLY on full success
        email_sent = False
        if send_email:
            publisher = EmailPublisher()
            preview_path = publisher.write_preview(edition, DEFAULT_EMAIL_PREVIEW_PATH)
            publisher.send(edition)
            email_sent = True
            LOGGER.info("Email sent to %s", publisher.config.recipient)

        complete()

        result = {
            "edition_path": str(DEFAULT_EDITION_PATH),
            "email_preview_path": str(preview_path),
            "email_sent": email_sent,
            "deployed_url": deployed_url,
            "version_hash": version_hash,
        }
        LOGGER.info("Generate stage complete: %s", result)
        return result

    except Exception as exc:
        stage_failed = True
        failure_reason = str(exc)
        LOGGER.exception("Generate stage failed: %s", exc)
        fail(failure_reason)

        # Alert admin on catastrophic failure
        _alert_admin(failure_reason)
        raise


def _run_all_sections(db_path: Path, adapter) -> dict[str, Any]:
    """Run all LLM section generators with graceful degradation.

    If a section fails after retries, logs ERROR, inserts sentinel value,
    and continues to the next section. If ALL sections fail, raises.
    """
    from pipeline.generators.biztech import generate_biztech
    from pipeline.generators.assembler import _prefetch_biztech_rows, _prefetch_news_rows

    results: dict[str, Any] = {}
    failed_sections: list[str] = []

    # News regions first — TLDR needs enriched articles (headline/summary)
    news_rows = _prefetch_news_rows(db_path)
    news_sections: dict[str, list] = {}
    for region in ["bangalore", "karnataka", "india", "us", "world"]:
        set_step(f"news_{region}")
        try:
            news_sections[region] = generate_news_region(
                news_rows.get(region, []),
                region=region,
                adapter=adapter,
            )
        except Exception as exc:
            LOGGER.error("News region '%s' failed: %s", region, exc)
            news_sections[region] = [{
                "_error": "generation_failed",
                "failed_section": f"news_{region}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": str(exc),
            }]
            failed_sections.append(f"news_{region}")
    results["news"] = news_sections

    # TLDR — called AFTER news so enriched articles (headline/summary) are available
    set_step("tldr")
    try:
        results["tldr"] = generate_tldr(news_sections, adapter=adapter)
    except Exception as exc:
        LOGGER.error("TLDR generation failed: %s", exc)
        results["tldr"] = {
            "_error": "generation_failed",
            "failed_section": "tldr",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": str(exc),
        }
        failed_sections.append("tldr")

    # Biz/Tech
    set_step("biztech")
    try:
        biztech_rows, indices = _prefetch_biztech_rows(db_path)
        results["biztech"] = generate_biztech(biztech_rows, indices, adapter=adapter)
    except Exception as exc:
        LOGGER.error("BizTech generation failed: %s", exc)
        results["biztech"] = {"_error": "generation_failed", "failed_section": "biztech", "timestamp": datetime.now(timezone.utc).isoformat(), "message": str(exc), "articles": []}
        failed_sections.append("biztech")

    # Growth
    set_step("growth")
    try:
        results["growth"] = generate_growth_section(adapter=adapter)
    except Exception as exc:
        LOGGER.error("Growth generation failed: %s", exc)
        results["growth"] = {"_error": "generation_failed", "failed_section": "growth", "timestamp": datetime.now(timezone.utc).isoformat(), "message": str(exc), "title": "Generation failed", "body": ""}
        failed_sections.append("growth")

    # Knowledge
    set_step("knowledge")
    try:
        results["knowledge"] = generate_knowledge_section(adapter=adapter)
    except Exception as exc:
        LOGGER.error("Knowledge generation failed: %s", exc)
        results["knowledge"] = {"_error": "generation_failed", "failed_section": "knowledge", "timestamp": datetime.now(timezone.utc).isoformat(), "message": str(exc), "title": "Generation failed", "body": ""}
        failed_sections.append("knowledge")

    # Fun
    set_step("fun")
    try:
        results["fun"] = generate_fun_section(adapter=adapter)
    except Exception as exc:
        LOGGER.error("Fun generation failed: %s", exc)
        results["fun"] = {"_error": "generation_failed", "failed_section": "fun", "timestamp": datetime.now(timezone.utc).isoformat(), "message": str(exc), "riddle": {}, "sudoku": {}, "chess": {}, "logic_puzzle": {}, "previous_day_answers": {}}
        failed_sections.append("fun")

    # If every section failed, abort rather than ship a broken edition
    all_sections = ["tldr", "news_bangalore", "news_karnataka", "news_india", "news_us", "news_world", "biztech", "growth", "knowledge", "fun"]
    if all(s in failed_sections for s in all_sections):
        raise RuntimeError(
            f"All {len(all_sections)} section generators failed: {failed_sections}. "
            "Pipeline aborted. Check API keys and data before re-running."
        )

    return results


def _build_edition(db_path: Path, sections: dict[str, Any]) -> dict[str, Any]:
    """Build the final edition dict from sections + metadata."""
    return {
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


def _write_edition(edition: dict[str, Any]) -> None:
    """Write edition.json to both data/ and web/public/data/."""
    DEFAULT_EDITION_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_EDITION_PATH.write_text(json.dumps(edition, indent=2))
    WEB_EDITION_PATH.parent.mkdir(parents=True, exist_ok=True)
    WEB_EDITION_PATH.write_text(json.dumps(edition, indent=2))


def main() -> None:
    """CLI entry point for the generate stage."""
    parser = argparse.ArgumentParser(description="News To Me — generate stage")
    parser.add_argument("--deploy", action="store_true", help="Deploy to Vercel after assembling")
    parser.add_argument("--no-email", action="store_true", help="Skip sending email (dev/debug)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable DEBUG logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    result = run(deploy=args.deploy, send_email=not args.no_email)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()