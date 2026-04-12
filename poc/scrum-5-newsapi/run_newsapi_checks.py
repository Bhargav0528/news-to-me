import json
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / 'samples'
SAMPLES.mkdir(parents=True, exist_ok=True)
API_KEY = '6f7c584aa7e44f2c80bcdb83e47fd6ef'

QUERIES = {
    'top_us_technology': f'https://newsapi.org/v2/top-headlines?country=us&category=technology&pageSize=5&apiKey={API_KEY}',
    'top_us_business': f'https://newsapi.org/v2/top-headlines?country=us&category=business&pageSize=5&apiKey={API_KEY}',
    'top_in_technology': f'https://newsapi.org/v2/top-headlines?country=in&category=technology&pageSize=5&apiKey={API_KEY}',
    'top_in_business': f'https://newsapi.org/v2/top-headlines?country=in&category=business&pageSize=5&apiKey={API_KEY}',
    'everything_india': f'https://newsapi.org/v2/everything?q=india&language=en&pageSize=5&sortBy=publishedAt&apiKey={API_KEY}',
    'everything_us': f'https://newsapi.org/v2/everything?q=usa&language=en&pageSize=5&sortBy=publishedAt&apiKey={API_KEY}',
}

for name, url in QUERIES.items():
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    (SAMPLES / f'{name}.json').write_text(json.dumps(data, indent=2))
    summary = {
        'status': data.get('status'),
        'totalResults': data.get('totalResults'),
        'articleCount': len(data.get('articles', [])),
        'sampleArticles': [
            {
                'title': a.get('title'),
                'source': (a.get('source') or {}).get('name'),
                'publishedAt': a.get('publishedAt'),
                'description': a.get('description'),
                'content': a.get('content'),
                'url': a.get('url'),
            }
            for a in data.get('articles', [])[:3]
        ],
    }
    (SAMPLES / f'{name}.summary.json').write_text(json.dumps(summary, indent=2))

print('Saved sample responses to', SAMPLES)
