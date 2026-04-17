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


def generate_news_sections(news_rows: dict[str, list], adapter=None) -> dict[str, list[dict[str, Any]]]:
    """Generate region-based news sections from pre-fetched rows using LLM.
    
    Args:
        news_rows: dict mapping region key (e.g. 'bangalore') to list of row dicts
                   with keys: title, url, source, category, region, excerpt, full_text, published_date
        adapter: LLM adapter (optional, builds default if not provided)
    """
    adapter = adapter or build_adapter(ModelConfig())
    
    result: dict[str, list[dict[str, Any]]] = {}
    
    for region, rows in news_rows.items():
        if not rows:
            result[region] = []
            continue
        
        # Prepare articles for batch LLM call
        articles = []
        for row in rows:
            # Handle both dict-like and plain dict row objects
            # sqlite3.Row supports row['key'] and row.keys() but NOT row.get()
            if hasattr(row, 'get'):
                # Plain dict
                title = row.get('title', '')
                source = row.get('source', '')
                region_val = row.get('region', '')
                category = row.get('category', '')
                full_text = row.get('full_text') or ''
                excerpt = row.get('excerpt') or ''
                url = row.get('url', '')
            elif hasattr(row, 'keys'):
                # sqlite3.Row or dict-like - use dict() conversion then .get
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
        
        # One LLM call per region
        prompt = _load_prompt("news_summary.txt")
        user = json.dumps(articles, ensure_ascii=False)
        
        try:
            llm_result = adapter.generate_json(prompt, user)
            summaries = llm_result if isinstance(llm_result, list) else llm_result.get('summaries', llm_result.get('articles', []))
            if len(summaries) != len(rows):
                summaries = _fallback_for_rows(rows)
        except Exception:
            summaries = _fallback_for_rows(rows)
        
        # Attach headline and source_url
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
        
        result[region] = summaries
    
    return result