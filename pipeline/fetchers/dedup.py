"""Title-based deduplication helpers for fetched news articles."""

from __future__ import annotations

from copy import deepcopy
from difflib import SequenceMatcher
from typing import Any

SIMILARITY_THRESHOLD = 0.8


def normalize_title(title: str) -> str:
    """Normalize a title for similarity comparison."""
    return " ".join((title or "").lower().split())


def title_similarity(left: str, right: str) -> float:
    """Return a normalized similarity score between two titles."""
    return SequenceMatcher(None, normalize_title(left), normalize_title(right)).ratio()


def _content_score(article: dict[str, Any]) -> int:
    """Score an article by available full text length, falling back to excerpt length."""
    full_text = article.get("full_text") or ""
    excerpt = article.get("excerpt") or ""
    return len(full_text.strip()) or len(excerpt.strip())


def deduplicate_articles(
    articles: list[dict[str, Any]],
    similarity_threshold: float = SIMILARITY_THRESHOLD,
) -> tuple[list[dict[str, Any]], int]:
    """Remove near-duplicate articles and keep the one with more content."""
    deduped: list[dict[str, Any]] = []
    duplicates_removed = 0

    for article in articles:
        replacement_index: int | None = None
        is_duplicate = False
        for index, existing in enumerate(deduped):
            if title_similarity(article.get("title", ""), existing.get("title", "")) < similarity_threshold:
                continue
            is_duplicate = True
            duplicates_removed += 1
            if _content_score(article) > _content_score(existing):
                replacement_index = index
            break
        if replacement_index is not None:
            deduped[replacement_index] = deepcopy(article)
        elif not is_duplicate:
            deduped.append(deepcopy(article))

    return deduped, duplicates_removed
