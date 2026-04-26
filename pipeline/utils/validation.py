"""Schema validation for edition.json.

Validates the assembled edition before commit/deploy/email to ensure
broken content is never shipped to the site or the reader.

Usage:
    from pipeline.utils.validation import validate_edition
    
    ok, errors = validate_edition(edition)
    if not ok:
        raise RuntimeError(f"Edition validation failed: {errors}")
"""

from __future__ import annotations

import logging
import re
import urllib.parse
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

REQUIRED_TOP_LEVEL_KEYS = [
    "date",
    "edition_number",
    "generated_at",
    "tldr",
    "news",
    "biztech",
    "growth",
    "knowledge",
    "fun",
]

REQUIRED_NEWS_REGIONS = ["bangalore", "karnataka", "india", "us", "world"]

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


def validate_edition(edition: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate an edition dict against the expected schema.

    Returns:
        (True, []) if valid.
        (False, [list of error strings]) if invalid.
    """
    errors: list[str] = []

    # 1. Top-level keys
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in edition:
            errors.append(f"Missing top-level key: '{key}'")

    # 2. date format
    date_val = edition.get("date", "")
    if date_val and not DATE_RE.match(date_val):
        errors.append(f"Invalid date format: '{date_val}' (expected YYYY-MM-DD)")

    # 3. generated_at format
    gen_at = edition.get("generated_at", "")
    if gen_at and not ISO_DATETIME_RE.match(gen_at):
        errors.append(f"Invalid generated_at format: '{gen_at}' (expected ISO datetime)")

    # 4. tldr — non-empty list
    tldr = edition.get("tldr")
    if tldr is None:
        errors.append("tldr is None")
    elif isinstance(tldr, list) and len(tldr) == 0:
        errors.append("tldr is an empty list")
    elif not isinstance(tldr, list):
        errors.append(f"tldr is not a list: {type(tldr).__name__}")

    # 5. news — all 5 regions present
    news = edition.get("news", {})
    if not isinstance(news, dict):
        errors.append(f"news is not a dict: {type(news).__name__}")
    else:
        for region in REQUIRED_NEWS_REGIONS:
            if region not in news:
                errors.append(f"news missing region: '{region}'")
            elif not isinstance(news[region], list):
                errors.append(f"news.{region} is not a list")
            elif len(news[region]) == 0:
                # Empty region is allowed (source may have had no articles)
                pass

    # 6. biztech.articles
    biztech = edition.get("biztech", {})
    if isinstance(biztech, dict):
        articles = biztech.get("articles", [])
        if not isinstance(articles, list):
            errors.append("biztech.articles is not a list")
    else:
        errors.append(f"biztech is not a dict: {type(biztech).__name__}")

    # 7. growth, knowledge, fun — dict-shaped
    for section in ["growth", "knowledge", "fun"]:
        if section not in edition:
            errors.append(f"Missing section: {section}")
        elif not isinstance(edition[section], dict):
            errors.append(f"{section} is not a dict: {type(edition[section]).__name__}")

    # 8. Check for generation_failed sentinel — only allowed as the ONLY content
    for section in REQUIRED_TOP_LEVEL_KEYS:
        section_data = edition.get(section)
        if isinstance(section_data, dict) and section_data.get("_error") == "generation_failed":
            # It's a failed section — allowed, but log it
            LOGGER.warning("Section '%s' has generation_failed sentinel", section)

    # 9. URL well-formedness in source_url fields
    all_articles = []
    for region, articles in edition.get("news", {}).items():
        all_articles.extend(articles)
    for article in all_articles:
        url = article.get("source_url", "")
        if url:
            try:
                urllib.parse.urlparse(url)
            except Exception:
                errors.append(f"Malformed URL in news article: {url}")

    return (len(errors) == 0, errors)


def validate_and_log(edition: dict[str, Any], output_dir: Path) -> bool:
    """Validate edition, log errors, write broken edition to disk if invalid.

    Args:
        edition: The edition dict to validate.
        output_dir: Directory to write broken editions to (e.g. data/broken_editions/).

    Returns:
        True if valid, False if invalid.
    """
    ok, errors = validate_edition(edition)
    if ok:
        LOGGER.info("Edition validation passed")
        return True

    LOGGER.error("Edition validation FAILED: %s", "; ".join(errors))

    # Write broken edition for debugging
    broken_dir = output_dir / "broken_editions"
    broken_dir.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    broken_path = broken_dir / f"edition_{timestamp}_broken.json"
    broken_path.write_text(
        "<!-- VALIDATION ERRORS: " + "; ".join(errors) + "-->\n" + __import__("json").dumps(edition, indent=2)
    )
    LOGGER.error("Broken edition written to: %s", broken_path)
    return False