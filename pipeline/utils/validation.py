"""Schema validation for edition.json.

Validates the assembled edition before commit/deploy/email to ensure
broken content is never shipped to the site or the reader.

Graceful degradation: a section with {"_error": "generation_failed", ...}
is VALID and not treated as a failure. The pipeline continues even if
one or more sections fail — only ALL sections failing is catastrophic.

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


def _is_sentinel(section_data: Any) -> bool:
    """Return True if section_data is a generation_failed sentinel dict."""
    return (
        isinstance(section_data, dict)
        and section_data.get("_error") == "generation_failed"
    )


def validate_edition(edition: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate an edition dict against the expected schema.

    A section with {"_error": "generation_failed", ...} is treated as valid —
    the graceful degradation sentinel, not a validation error.

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

    # 4. tldr — non-empty list OR generation_failed sentinel
    tldr = edition.get("tldr")
    if tldr is None:
        errors.append("tldr is None")
    elif _is_sentinel(tldr):
        LOGGER.warning("tldr has generation_failed sentinel")
    elif not isinstance(tldr, list):
        errors.append(f"tldr is not a list: {type(tldr).__name__}")
    elif len(tldr) == 0:
        errors.append("tldr is an empty list")

    # 5. news — all 5 regions present (each is a list OR sentinel)
    news = edition.get("news", {})
    if not isinstance(news, dict):
        errors.append(f"news is not a dict: {type(news).__name__}")
    else:
        for region in REQUIRED_NEWS_REGIONS:
            if region not in news:
                errors.append(f"news missing region: '{region}'")
            elif not isinstance(news[region], list):
                # Region value is not a list — could be a sentinel
                errors.append(f"news.{region} is not a list")

    # 6. biztech.articles — list OR sentinel
    biztech = edition.get("biztech", {})
    if _is_sentinel(biztech):
        LOGGER.warning("biztech has generation_failed sentinel")
    elif not isinstance(biztech, dict):
        errors.append(f"biztech is not a dict: {type(biztech).__name__}")
    else:
        articles = biztech.get("articles", [])
        if not isinstance(articles, list):
            errors.append("biztech.articles is not a list")

    # 7. growth, knowledge, fun — dict-shaped OR sentinel
    for section in ["growth", "knowledge", "fun"]:
        section_data = edition.get(section)
        if section_data is None:
            errors.append(f"{section} is None")
        elif _is_sentinel(section_data):
            LOGGER.warning("%s has generation_failed sentinel", section)
        elif not isinstance(section_data, dict):
            errors.append(f"{section} is not a dict: {type(section_data).__name__}")

    # 8. news sub-region values — each must be a list OR sentinel
    for region in REQUIRED_NEWS_REGIONS:
        region_data = edition.get("news", {}).get(region)
        if region_data is None:
            continue  # already reported as missing above
        if isinstance(region_data, list):
            pass  # valid
        elif _is_sentinel(region_data):
            pass  # valid — region failed gracefully
        else:
            errors.append(f"news.{region} is not a list (got {type(region_data).__name__})")

    # 9. URL well-formedness in source_url fields (skip sentinel articles)
    all_articles = []
    for region, articles in edition.get("news", {}).items():
        if _is_sentinel(articles):
            continue
        all_articles.extend(articles)
    for article in all_articles:
        if _is_sentinel(article):
            continue
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