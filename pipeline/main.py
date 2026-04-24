"""Thin dev orchestrator for the News To Me pipeline.

This module exists for local development convenience only.
It runs ingest then generate sequentially in one process.

WARNING: In constrained execution environments (e.g., agent sandboxes with
short SIGKILL timeouts), this may be terminated mid-run.
For production use, run the two stages separately:

    python3 -m pipeline.ingest    # fast, safe everywhere
    python3 -m pipeline.generate  # slow, needs full budget

See README.md for the full pipeline architecture documentation.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

from pipeline.ingest import run as run_ingest
from pipeline.generate import run as run_generate

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Run ingest then generate sequentially (dev convenience only).

    In production, run the two stages separately via cron or a CI runner
    that has a longer timeout budget.
    """
    parser = argparse.ArgumentParser(
        description=(
            "News To Me pipeline (dev convenience wrapper).\n"
            "WARNING: This may SIGKILL in constrained environments.\n"
            "For production, run: python3 -m pipeline.ingest && python3 -m pipeline.generate"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--article-limit", type=int, default=None)
    parser.add_argument("--deploy", action="store_true", help="Deploy to Vercel (generate stage only)")
    parser.add_argument("--send-email", action="store_true", help="Send email after generate")
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Skip ingest stage (use existing DB data)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    print("=" * 60)
    print(" WARNING: pipeline/main.py is for LOCAL DEV only.")
    print(" For production, run ingest and generate separately.")
    print("=" * 60)

    # Stage 1: ingest
    if args.skip_ingest:
        print("\n[1/2] Skipping ingest (--skip-ingest set)")
        ingest_result = None
    else:
        print("\n[1/2] Running ingest stage...")
        ingest_result = run_ingest(article_limit=args.article_limit)
        print(f"  → Ingest complete: {ingest_result['articles_inserted']} articles inserted")

    # Stage 2: generate
    print("\n[2/2] Running generate stage...")
    generate_result = run_generate(
        deploy=args.deploy,
        send_email=args.send_email,
    )
    print(f"  → Generate complete: edition at {generate_result['edition_path']}")
    if generate_result.get("deployed_url"):
        print(f"  → Deployed: {generate_result['deployed_url']}")
    if generate_result.get("email_sent"):
        print(f"  → Email sent")

    print("\nDone.")


if __name__ == "__main__":
    main()
