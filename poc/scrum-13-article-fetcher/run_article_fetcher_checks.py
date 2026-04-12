from __future__ import annotations

import json
import statistics
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.fetchers.article_fetcher import ArticleFetcher

RSS_RESULTS_PATH = ROOT / "poc" / "scrum-6-rss" / "rss_results.json"
OUTPUT_DIR = ROOT / "poc" / "scrum-13-article-fetcher"
RESULTS_PATH = OUTPUT_DIR / "article_fetch_results.json"
COMPARISONS_PATH = OUTPUT_DIR / "excerpt_vs_fulltext.json"
SUMMARY_PATH = OUTPUT_DIR / "summary.json"

TARGET_SOURCES = [
    "The Hindu",
    "Indian Express India",
    "The Hindu BusinessLine",
    "BBC World",
    "NPR World",
    "NYT Home",
    "CNBC Top News",
    "MarketWatch Top Stories",
    "TechCrunch",
    "Ars Technica",
]


def load_rss_descriptions(feed_result):
    xml_path = ROOT / "poc" / "scrum-6-rss" / feed_result["raw_xml_path"]
    root = ET.fromstring(xml_path.read_text())
    descriptions = {}
    for item in root.findall("./channel/item"):
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        if link:
            descriptions[link] = description
    return descriptions


def pick_test_articles():
    data = json.loads(RSS_RESULTS_PATH.read_text())
    selected = []
    seen_urls = set()
    for source_name in TARGET_SOURCES:
        feed_result = next((item for item in data if item["feed"]["name"] == source_name), None)
        if not feed_result:
            continue
        descriptions = load_rss_descriptions(feed_result)
        for entry in feed_result.get("sample_entries", []):
            url = entry["link"]
            if url in seen_urls:
                continue
            seen_urls.add(url)
            excerpt = descriptions.get(url, "")
            selected.append(
                {
                    "source": source_name,
                    "title": entry["title"],
                    "url": url,
                    "excerpt": excerpt,
                    "summary_words": entry.get("summary_words", 0),
                    "content_type": entry.get("content_type"),
                }
            )
            break
    return selected[:10]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    articles = pick_test_articles()
    fetcher = ArticleFetcher(delay_seconds=1.1)
    enriched = fetcher.enrich_records(articles)

    RESULTS_PATH.write_text(json.dumps(enriched, indent=2, ensure_ascii=False))

    comparisons = []
    for item in enriched:
        excerpt = item.get("excerpt", "")
        if item.get("full_text") and excerpt:
            comparisons.append(
                {
                    "source": item["source"],
                    "title": item["title"],
                    "url": item["url"],
                    "excerpt": excerpt,
                    "excerpt_length": len(excerpt),
                    "full_text_preview": item["full_text"][:1800],
                    "full_text_length": item["full_text_length"],
                }
            )
        if len(comparisons) == 3:
            break
    COMPARISONS_PATH.write_text(json.dumps(comparisons, indent=2, ensure_ascii=False))

    successes = [item for item in enriched if item["fetch_status"] == "ok"]
    failures = [item for item in enriched if item["fetch_status"] != "ok"]
    methods = {}
    for item in successes:
        methods[item["fetch_method"]] = methods.get(item["fetch_method"], 0) + 1

    summary = {
        "tested_url_count": len(enriched),
        "success_count": len(successes),
        "failure_count": len(failures),
        "success_rate": round(len(successes) / len(enriched), 3) if enriched else 0,
        "average_full_text_length": round(statistics.mean([item["full_text_length"] for item in successes]), 1) if successes else 0,
        "best_method_by_count": max(methods, key=methods.get) if methods else None,
        "method_counts": methods,
        "blocked_or_paywalled": [
            {
                "source": item["source"],
                "url": item["url"],
                "http_status": item["http_status"],
                "fetch_error": item["fetch_error"],
            }
            for item in failures
            if item.get("http_status") in {401, 402, 403, 406, 410, 429, 451}
        ],
        "failures": [
            {
                "source": item["source"],
                "url": item["url"],
                "http_status": item["http_status"],
                "fetch_error": item["fetch_error"],
            }
            for item in failures
        ],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
