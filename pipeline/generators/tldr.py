"""TLDR generation helpers for the News To Me pipeline."""

from __future__ import annotations

from typing import Any

from pipeline.generators.engine import build_adapter, ModelConfig


def _row_to_dict(row) -> dict:
    """Convert sqlite3.Row to plain dict."""
    return dict(row) if not isinstance(row, dict) else row


def generate_tldr(news_sections: dict[str, list[dict[str, Any]]], adapter=None) -> list[dict[str, Any]]:
    """Build the cross-section TLDR list using LLM for distillation."""
    adapter = adapter or build_adapter(ModelConfig())
    
    # Collect lead articles from each region
    items = []
    region_order = ['bangalore', 'karnataka', 'india', 'us', 'world']
    for region in region_order:
        articles = news_sections.get(region, [])
        if not articles:
            continue
        lead = _row_to_dict(articles[0])
        items.append({
            'headline': lead.get('headline', ''),
            'summary': lead.get('summary', ''),
            'region': region,
            'category': lead.get('category', 'top'),
        })
        if len(items) >= 7:
            break
    
    if not items:
        return []
    
    # Use LLM to pick top 5-7 and write 2-3 line summaries
    system_prompt = """You are a news editor creating a TLDR section for a personal daily newspaper.
Select the 5-7 most important stories across all regions and write 2-3 sentence summaries.
Prioritize stories that matter to a 28-year-old South Indian developer in California.
Return a JSON array of objects with: headline (max 15 words), summary (2-3 sentences), region, category."""
    
    user = f"Stories:\n{items}"
    
    try:
        result = adapter.generate_json(system_prompt, user)
        tldr_list = result if isinstance(result, list) else result.get('tldr', result.get('stories', items))
        # Ensure region and category are set
        for item in tldr_list:
            if 'region' not in item:
                item['region'] = item.get('region', 'world')
            if 'category' not in item:
                item['category'] = item.get('category', 'top')
        return tldr_list[:7]
    except Exception:
        # Fallback: return raw items with truncated summaries
        for item in items:
            if len(item.get('summary', '')) > 240:
                item['summary'] = item['summary'][:240] + '...'
        return items[:7]