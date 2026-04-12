#!/usr/bin/env python3
import json
import re
import html
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
import xml.etree.ElementTree as ET

import requests

FEEDS = [
    {"name": "The Hindu", "category": "India / General", "url": "https://www.thehindu.com/feeder/default.rss"},
    {"name": "Indian Express India", "category": "India / National", "url": "https://indianexpress.com/section/india/feed/"},
    {"name": "The Hindu BusinessLine", "category": "India / Business", "url": "https://www.thehindubusinessline.com/feeder/default.rss"},
    {"name": "BBC World", "category": "World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "NPR World", "category": "World", "url": "https://feeds.npr.org/1004/rss.xml"},
    {"name": "NYT Home", "category": "US / General", "url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"},
    {"name": "CNBC Top News", "category": "US / Business", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html"},
    {"name": "MarketWatch Top Stories", "category": "US / Markets", "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories"},
    {"name": "TechCrunch", "category": "Tech", "url": "https://techcrunch.com/feed/"},
    {"name": "Ars Technica", "category": "Tech", "url": "https://feeds.arstechnica.com/arstechnica/index"},
]

NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "atom": "http://www.w3.org/2005/Atom",
}


def strip_html(text: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_dt(value: str | None):
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def text_of(elem, path, ns=None):
    found = elem.find(path, ns or {})
    if found is None:
        return None
    return (found.text or "").strip() or None


def classify_text(summary: str, content: str):
    s_len = len(summary.split()) if summary else 0
    c_len = len(content.split()) if content else 0
    if c_len >= 250:
        return "likely full article text"
    if c_len >= 120:
        return "long excerpt"
    if s_len >= 80:
        return "rich excerpt"
    if s_len or c_len:
        return "headline + short excerpt"
    return "headline/link only"


def analyze_feed(session: requests.Session, feed):
    url = feed["url"]
    resp = session.get(url, timeout=20, headers={"User-Agent": "news-to-me-poc/0.1"}, allow_redirects=True)
    resp.raise_for_status()
    raw = resp.text
    root = ET.fromstring(raw)

    channel = root.find("channel")
    items = []
    if channel is not None:
        items = channel.findall("item")
    if not items:
        items = root.findall(".//item")

    entries = []
    for item in items[:15]:
        title = text_of(item, "title") or ""
        link = text_of(item, "link") or text_of(item, "atom:link", NS) or ""
        summary = text_of(item, "description") or text_of(item, "summary") or ""
        content = text_of(item, "content:encoded", NS) or ""
        published = (
            text_of(item, "pubDate")
            or text_of(item, "published")
            or text_of(item, "dc:date", NS)
            or text_of(item, "dc:creator", NS)
        )
        published_dt = parse_dt(published)
        entries.append(
            {
                "title": strip_html(title),
                "link": link.strip(),
                "summary": strip_html(summary),
                "content": strip_html(content),
                "published": published_dt.isoformat() if published_dt else None,
            }
        )

    now = datetime.now(timezone.utc)
    dated = [e for e in entries if e["published"]]
    dated_dts = [datetime.fromisoformat(e["published"]) for e in dated]
    newest = max(dated_dts) if dated_dts else None
    per_day = sum(1 for dt in dated_dts if (now - dt).total_seconds() <= 86400)

    statuses = [classify_text(e["summary"], e["content"]) for e in entries[:5]]
    status_counts = {}
    for s in statuses:
        status_counts[s] = status_counts.get(s, 0) + 1

    sample = []
    for e in entries[:5]:
        sample.append(
            {
                "title": e["title"],
                "published": e["published"],
                "summary_words": len(e["summary"].split()),
                "content_words": len(e["content"].split()),
                "content_type": classify_text(e["summary"], e["content"]),
                "link": e["link"],
            }
        )

    reliability = "good" if len(entries) >= 10 and resp.status_code == 200 else "mixed"
    freshness = None
    if newest:
        freshness = round((now - newest).total_seconds() / 3600, 2)

    return {
        "feed": feed,
        "http_status": resp.status_code,
        "final_url": resp.url,
        "item_count_in_feed": len(items),
        "items_sampled": len(entries),
        "articles_in_last_24h_with_timestamp": per_day,
        "freshness_hours_since_newest": freshness,
        "reliability": reliability,
        "sample_content_types": status_counts,
        "sample_entries": sample,
        "raw_xml_path": None,
    }, raw


def main():
    base = Path(__file__).resolve().parent
    samples = base / "samples"
    samples.mkdir(parents=True, exist_ok=True)
    out = []
    session = requests.Session()
    for feed in FEEDS:
        slug = re.sub(r"[^a-z0-9]+", "-", feed["name"].lower()).strip("-")
        try:
            data, raw = analyze_feed(session, feed)
            xml_path = samples / f"{slug}.xml"
            xml_path.write_text(raw)
            data["raw_xml_path"] = str(xml_path.relative_to(base))
            (samples / f"{slug}.summary.json").write_text(json.dumps(data, indent=2))
            out.append(data)
            print(f"OK  {feed['name']}")
        except Exception as e:
            fail = {
                "feed": feed,
                "error": str(e),
                "reliability": "failed",
            }
            (samples / f"{slug}.summary.json").write_text(json.dumps(fail, indent=2))
            out.append(fail)
            print(f"ERR {feed['name']}: {e}")
    (base / "rss_results.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
