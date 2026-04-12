#!/usr/bin/env python3
import datetime as dt
import html
import json
import pathlib
import sqlite3
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent
POC = ROOT.parent
FOUNDATION_DB = POC / 'scrum-2-foundation' / 'sample_output' / 'news_to_me.db'
MARKETS_PATH = POC / 'scrum-7-stock-data' / 'stock_results.json'
OUTPUT_DIR = ROOT / 'sample_output'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SECTION_SPECS = [
    ('tldr', 'TLDR', None, None, 4),
    ('india', 'India', 'india', 'top', 5),
    ('world', 'World', 'world', 'top', 5),
    ('us', 'US', 'us', 'top', 5),
    ('business', 'Business', 'us', 'business', 5),
    ('technology', 'Technology', 'us', 'technology', 5),
    ('markets', 'Markets', None, None, 4),
]

SOURCE_PRIORITY = {
    'nyt-home': 100,
    'bbc-world': 95,
    'the-hindu-general': 92,
    'npr-world': 88,
    'cnbc-top-news': 84,
    'businessline-markets': 82,
    'techcrunch': 80,
    'ars-technica': 78,
    'indian-express-india': 76,
}

BANNED_SNIPPETS = [
    'live updates', 'watch live', 'photos:', 'podcast', 'crossword', 'horoscope', 'quiz', 'where to watch'
]


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def score_article(row: sqlite3.Row) -> int:
    title = (row['title'] or '').lower()
    excerpt = (row['excerpt'] or '').lower()
    score = SOURCE_PRIORITY.get(row['source_id'], 50)
    score += min(len(row['title'] or ''), 120) // 8
    score += min(len(row['excerpt'] or ''), 240) // 24
    for bad in BANNED_SNIPPETS:
        if bad in title or bad in excerpt:
            score -= 25
    if 'analysis' in title:
        score -= 4
    return score


def clean_excerpt(text: str) -> str:
    text = ' '.join((text or '').split())
    return text[:220].rstrip() + ('…' if len(text) > 220 else '')


def fetch_articles(conn: sqlite3.Connection, region: str, section: str, limit: int):
    rows = list(conn.execute(
        '''
        SELECT title, url, source_id, region, section, published_at, excerpt
        FROM articles
        WHERE region = ? AND section = ?
        ''',
        (region, section),
    ))
    ranked = sorted(rows, key=lambda r: (-score_article(r), r['published_at'] or '', r['title'] or ''))
    selected = []
    seen = set()
    for row in ranked:
        title_key = ' '.join((row['title'] or '').lower().split())
        if title_key in seen:
            continue
        seen.add(title_key)
        selected.append({
            'title': row['title'],
            'url': row['url'],
            'source': row['source_id'],
            'published_at': row['published_at'],
            'excerpt': clean_excerpt(row['excerpt'] or ''),
            'score': score_article(row),
        })
        if len(selected) >= limit:
            break
    return selected


def build_tldr(section_map):
    candidates = []
    for key in ['india', 'world', 'us', 'business', 'technology']:
        candidates.extend(section_map[key]['stories'][:1])
    sources = Counter(item['source'] for item in candidates)
    return {
        'headline': 'A real 7-section edition is now reproducible from saved intake artifacts',
        'summary': (
            'The generate-and-publish spike can now assemble a full morning edition from the saved Sprint 1 foundation database plus the validated market snapshot. '
            'The strongest packet is still hard-news led by top-tier RSS sources, while business and technology quality remains more sensitive to source mix.'
        ),
        'why_it_matters': (
            'This de-risks Sprint 2 at the pipeline level: intake artifacts can be turned into a readable edition shape without inventing fake data or needing deploy access first.'
        ),
        'stories_used': [item['title'] for item in candidates],
        'source_mix': dict(sources),
    }


def build_section(section_id, label, stories):
    lead = 'No stories available.'
    if stories:
        lead = f"{label} is currently led by {stories[0]['title']}"
        if len(stories) > 1:
            lead += f", with {stories[1]['title']} also shaping the read."
        else:
            lead += '.'
    bullets = []
    for story in stories[:3]:
        bullets.append(f"{story['title']} ({story['source']})")
    return {
        'id': section_id,
        'label': label,
        'lead': lead,
        'story_count': len(stories),
        'stories': stories,
        'summary_points': bullets,
    }


def load_markets():
    data = json.loads(MARKETS_PATH.read_text())
    run = data['runs'][-1]['yfinance']
    items = []
    for key, label in [('sp500', 'S&P 500'), ('nasdaq', 'NASDAQ'), ('nifty50', 'NIFTY 50'), ('sensex', 'SENSEX')]:
        row = run[key]
        items.append({
            'label': label,
            'symbol': row['source_symbol'],
            'value': row['value'],
            'change': row['change'],
            'change_percent': row['change_percent'],
            'currency': row['currency'],
            'as_of': row['as_of'],
        })
    return items


def render_html(edition):
    sections_html = []
    for section in edition['sections']:
        if section['id'] == 'markets':
            market_rows = ''.join(
                f"<li><strong>{m['label']}</strong>: {m['value']:.2f} {m['currency']} ({m['change']:+.2f}, {m['change_percent']:.2f}%)</li>"
                for m in section['stories']
            )
            body = f"<ul>{market_rows}</ul>"
        else:
            story_rows = ''.join(
                (
                    f"<li>{('<a href=\'' + html.escape(s['url']) + '\'>' + html.escape(s['title']) + '</a>') if s['url'] else html.escape(s['title'])} "
                    f"<span class='muted'>[{html.escape(s['source'])}]</span><br>{html.escape(s['excerpt'])}</li>"
                )
                for s in section['stories']
            )
            body = f"<p>{html.escape(section['lead'])}</p><ul>{story_rows}</ul>"
        sections_html.append(f"<section class='card'><h2>{html.escape(section['label'])}</h2>{body}</section>")

    return f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>News To Me, SCRUM-3 spike</title>
  <style>
    body {{ font-family: Inter, system-ui, sans-serif; max-width: 980px; margin: 0 auto; padding: 24px; background: #f5f1e8; color: #1b1b1b; line-height: 1.5; }}
    .hero, .card {{ background: #fffdf8; border: 1px solid #d7cfbf; border-radius: 14px; padding: 18px 20px; margin: 16px 0; box-shadow: 0 1px 0 rgba(0,0,0,0.03); }}
    h1, h2 {{ margin: 0 0 8px 0; }}
    ul {{ padding-left: 20px; }}
    .muted {{ color: #6a6258; }}
  </style>
</head>
<body>
  <section class='hero'>
    <h1>News To Me</h1>
    <p class='muted'>SCRUM-3 generate + publish spike, generated {html.escape(edition['generated_at'])}</p>
    <h2>{html.escape(edition['tldr']['headline'])}</h2>
    <p>{html.escape(edition['tldr']['summary'])}</p>
    <p><strong>Why it matters:</strong> {html.escape(edition['tldr']['why_it_matters'])}</p>
  </section>
  {''.join(sections_html)}
</body>
</html>
"""


def main():
    conn = sqlite3.connect(FOUNDATION_DB)
    conn.row_factory = sqlite3.Row

    section_map = {}
    sections = []
    for section_id, label, region, section, limit in SECTION_SPECS:
        if section_id == 'markets':
            market_items = load_markets()
            payload = {
                'id': 'markets',
                'label': 'Markets',
                'lead': 'Indices-only market snapshot from the validated Yahoo Finance path.',
                'story_count': len(market_items),
                'stories': market_items,
                'summary_points': [],
            }
        elif section_id == 'tldr':
            payload = {'id': 'tldr', 'label': 'TLDR', 'lead': '', 'story_count': 0, 'stories': [], 'summary_points': []}
        else:
            payload = build_section(section_id, label, fetch_articles(conn, region, section, limit))
        section_map[section_id] = payload

    tldr = build_tldr(section_map)
    section_map['tldr'] = {
        'id': 'tldr',
        'label': 'TLDR',
        'lead': tldr['summary'],
        'story_count': len(tldr['stories_used']),
        'stories': [{'title': title, 'url': '', 'source': 'multi-source', 'excerpt': '', 'score': None} for title in tldr['stories_used']],
        'summary_points': [tldr['why_it_matters']],
    }

    for section_id, *_ in SECTION_SPECS:
        sections.append(section_map[section_id])

    edition = {
        'generated_at': now_iso(),
        'ticket': 'SCRUM-3',
        'inputs': {
            'foundation_db': str(FOUNDATION_DB.relative_to(ROOT.parent.parent)),
            'markets': str(MARKETS_PATH.relative_to(ROOT.parent.parent)),
        },
        'tldr': tldr,
        'section_order': [label for _, label, _, _, _ in SECTION_SPECS],
        'sections': sections,
        'quality_notes': [
            'All editorial sections were populated from real saved intake rows in the Sprint 1 foundation SQLite database.',
            'Markets used the validated Yahoo Finance snapshot from SCRUM-7.',
            'This spike proves renderability and section assembly, not final production-level ranking or LLM writing quality.',
            'Deployment is still pending environment access, so this artifact remains a local static output proof.'
        ],
    }

    diagnostics = {
        'generated_at': edition['generated_at'],
        'section_story_counts': {section['label']: section['story_count'] for section in sections},
        'top_sources_used': Counter(
            story['source']
            for section in sections if section['id'] not in {'markets', 'tldr'}
            for story in section['stories']
        ),
    }
    diagnostics['top_sources_used'] = dict(diagnostics['top_sources_used'])

    (OUTPUT_DIR / 'edition.json').write_text(json.dumps(edition, indent=2))
    (OUTPUT_DIR / 'diagnostics.json').write_text(json.dumps(diagnostics, indent=2))
    (OUTPUT_DIR / 'index.html').write_text(render_html(edition))
    print(json.dumps(diagnostics, indent=2))


if __name__ == '__main__':
    main()
