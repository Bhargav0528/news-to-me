"""Business and technology section generation helpers."""

from __future__ import annotations

from typing import Any

from pipeline.generators.engine import build_adapter, ModelConfig


def _clean_text(text: str, max_chars: int = 3000) -> str:
    """Strip whitespace and cap article text length for LLM context window."""
    return ' '.join(text.strip().split())[:max_chars]


def _row_to_dict(row) -> dict:
    """Convert sqlite3.Row or dict to plain dict."""
    if hasattr(row, 'get'):
        return row  # already a dict
    if hasattr(row, 'keys'):
        return dict(row)
    return {}


def generate_biztech(biztech_rows: list, indices: list, adapter=None) -> dict[str, Any]:
    """Generate market snapshot and business/tech article packets via LLM."""
    adapter = adapter or build_adapter(ModelConfig())
    
    articles = []
    for row in biztech_rows:
        d = _row_to_dict(row)
        title = d.get('title', '')
        url = d.get('url', '')
        category = d.get('category', '')
        full_text = d.get('full_text') or ''
        excerpt = d.get('excerpt') or ''
        
        text = _clean_text(full_text or excerpt)
        if not text:
            articles.append({
                'headline': title,
                'summary': '',
                'market_impact': f"Affects {category} sector.",
                'source_url': url,
            })
            continue
        
        if len(text) > 50:
            try:
                prompt = """For this business/tech article, return JSON with:
- headline: the article title
- summary: 150-250 word summary
- market_impact: 1-2 sentences on how this affects markets/investors

Return valid JSON only."""
                result = adapter.generate_json(prompt, f"Title: {title}\n\nContent: {text}")
                articles.append({
                    'headline': result.get('headline', title),
                    'summary': result.get('summary', text[:250]),
                    'market_impact': result.get('market_impact', f"Affects {category} sector."),
                    'source_url': url,
                })
            except Exception:
                articles.append({
                    'headline': title,
                    'summary': text[:250],
                    'market_impact': f"May affect investor sentiment around {category}.",
                    'source_url': url,
                })
        else:
            articles.append({
                'headline': title,
                'summary': text[:250],
                'market_impact': f"Affects {category} sector.",
                'source_url': url,
            })
    
    return {
        'market_snapshot': {'indices': indices},
        'articles': articles,
    }