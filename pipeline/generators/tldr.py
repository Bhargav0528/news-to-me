"""TLDR generation helpers for the News To Me pipeline."""

from __future__ import annotations

from typing import Any


def generate_tldr(news_sections: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Build the cross-section TLDR list from the lead story in each region."""
    items: list[dict[str, Any]] = []
    for region, articles in news_sections.items():
        if not articles:
            continue
        lead = articles[0]
        items.append(
            {
                'headline': lead['headline'][:120],
                'summary': lead['summary'][:240],
                'region': region,
                'category': 'top',
            }
        )
        if len(items) >= 7:
            break
    return items
