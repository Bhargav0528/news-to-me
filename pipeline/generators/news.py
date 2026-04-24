"""News section generation helpers for the News To Me pipeline."""

from __future__ import annotations

import json
from typing import Any

from pipeline.generators.engine import build_adapter, ModelConfig


def _load_prompt(name: str) -> str:
    """Load a prompt template file."""
    from pathlib import Path
    return (Path(__file__).parent / "prompts" / name).read_text().strip()


def _clean_text(text: str, max_chars: int = 3000) -> str:
    """Strip whitespace and cap article text length for LLM context window."""
    return ' '.join(text.strip().split())[:max_chars]


def _fallback_for_rows(rows: list) -> list[dict[str, Any]]:
    """Generate fallback summaries when LLM fails."""
    results = []
    for row in rows:
        if hasattr(row, 'get'):
            text = _clean_text(row.get('full_text') or row.get('excerpt') or '')
            results.append({
                'summary': text[:250],
                'why_it_matters': f"Relevant for {row.get('region', 'readers')}.",
                'what_to_watch': 'Watch for follow-up reporting.',
                'public_reactions': 'Public reaction forming.',
                'context': f"Source: {row.get('source', 'news')}.",
            })
        elif hasattr(row, 'keys'):
            d = dict(row)
            text = _clean_text(d.get('full_text') or d.get('excerpt') or '')
            results.append({
                'summary': text[:250],
                'why_it_matters': f"Relevant for {d.get('region', 'readers')}.",
                'what_to_watch': 'Watch for follow-up reporting.',
                'public_reactions': 'Public reaction forming.',
                'context': f"Source: {d.get('source', 'news')}.",
            })
        else:
            results.append({
                'summary': '',
                'why_it_matters': 'Relevant news item.',
                'what_to_watch': 'Watch for follow-up reporting.',
                'public_reactions': 'Public reaction forming.',
                'context': 'News source.',
            })
    return results


def generate_news_region(
    rows: list,
    region: str,
    adapter=None,
) -> list[dict[str, Any]]:
    """Generate news summaries for a single region.

    Args:
        rows: List of row dicts for this region only.
        region: Region name (e.g. 'bangalore'), used in fallback messages only.
        adapter: LLM adapter (optional, builds default if not provided).

    Returns:
        List of summary dicts, one per input row.
    """
    adapter = adapter or build_adapter(ModelConfig())

    if not rows:
        return []

    articles = []
    for row in rows:
        if hasattr(row, 'get'):
            title = row.get('title', '')
            source = row.get('source', '')
            region_val = row.get('region', '')
            category = row.get('category', '')
            full_text = row.get('full_text') or ''
            excerpt = row.get('excerpt') or ''
            url = row.get('url', '')
        elif hasattr(row, 'keys'):
            d = dict(row)
            title = d.get('title', '')
            source = d.get('source', '')
            region_val = d.get('region', '')
            category = d.get('category', '')
            full_text = d.get('full_text') or ''
            excerpt = d.get('excerpt') or ''
            url = d.get('url', '')
        else:
            title = ''
            source = ''
            region_val = ''
            category = ''
            full_text = ''
            excerpt = ''
            url = ''

        articles.append({
            'title': title,
            'source': source,
            'region': region_val,
            'category': category,
            'url': url,
            'content': _clean_text(full_text or excerpt),
        })

    prompt = _load_prompt("news_summary.txt")
    user = json.dumps(articles, ensure_ascii=False)

    try:
        llm_result = adapter.generate_json(prompt, user)
        summaries = (
            llm_result
            if isinstance(llm_result, list)
            else llm_result.get('summaries', llm_result.get('articles', []))
        )
        if len(summaries) != len(rows):
            summaries = _fallback_for_rows(rows)
    except Exception:
        summaries = _fallback_for_rows(rows)

    for s, row in zip(summaries, rows):
        if hasattr(row, 'get'):
            s['headline'] = row.get('title', '')
            s['source_url'] = row.get('url', '')
        elif hasattr(row, 'keys'):
            d = dict(row)
            s['headline'] = d.get('title', '')
            s['source_url'] = d.get('url', '')
        else:
            s['headline'] = ''
            s['source_url'] = ''

    return summaries


def generate_news_sections(
    news_rows: dict[str, list],
    adapter=None,
) -> dict[str, list[dict[str, Any]]]:
    """Generate region-based news sections from pre-fetched rows using LLM.

    Args:
        news_rows: dict mapping region key (e.g. 'bangalore') to list of row dicts
                   with keys: title, url, source, category, region, excerpt, full_text, published_date
        adapter: LLM adapter (optional, builds default if not provided)

    Note: prefer generate_news_region() in generate.py to get per-step status tracking.
    """
    result: dict[str, list[dict[str, Any]]] = {}
    for region, rows in news_rows.items():
        result[region] = generate_news_region(rows, region, adapter)
    return result