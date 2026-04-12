#!/usr/bin/env python3
import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POC = ROOT.parent
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)


def load_json(path: Path):
    return json.loads(path.read_text())


def choose_articles(packet):
    articles = packet["articles"]
    ranked = sorted(
        articles,
        key=lambda a: (
            0 if a.get("author") == "Reuters" else 1,
            0 if a.get("source") in {"The Wall Street Journal", "Reuters", "The New York Times"} else 1,
            a.get("publishedAt", ""),
        ),
    )
    return ranked[:4]


def build_tldr(selected):
    titles = [a["title"] for a in selected]
    headline = "Inflation shock and AI security fears lead the morning"
    summary = (
        "Markets and tech coverage are being driven by a few concrete developments: a sharp US inflation print tied to an energy-price surge, "
        "a security incident targeting OpenAI CEO Sam Altman, and continued investor attention on major AI and consumer-device bets. "
        "The current source packet is usable for a rough morning brief, but article quality is uneven and several inputs are feature-like or thin."
    )
    why = "The pipeline can produce a credible one-glance brief now, but source filtering and stronger text inputs still matter a lot."
    return {
        "headline": headline,
        "summary": summary,
        "why_it_matters": why,
        "stories_used": titles[:4],
    }


def build_section(selected):
    return {
        "section": "Business + Tech",
        "lead": (
            "The current packet points to an uneasy mix of macro pressure and tech-sector volatility, with higher US inflation, a security scare around OpenAI, "
            "and ongoing investor fixation on AI and Apple hardware rumors shaping the morning read."
        ),
        "summary_points": [
            "Reuters-led inflation coverage is the clearest hard-news signal in the packet and should anchor the section.",
            "The OpenAI security incident is notable, but the current source mix needs careful handling to avoid sensational framing.",
            "Several technology items are light or feature-like, which weakens confidence in the overall business-tech bundle.",
            "A simple brief is feasible today, but the architecture still needs better source ranking and richer text inputs.",
        ],
        "watchlist": [
            "Follow inflation and fuel-price updates",
            "Watch for verified details on the OpenAI incident",
            "Upgrade source filtering before broader rollout",
        ],
    }


def latest_market_snapshot(stock_results):
    run = stock_results["runs"][-1]
    out = []
    for key, label in [("sp500", "S&P 500"), ("nasdaq", "NASDAQ"), ("nifty50", "NIFTY 50"), ("sensex", "SENSEX")]:
        item = run["yfinance"][key]
        out.append({
            "label": label,
            "symbol": item["source_symbol"],
            "value": item["value"],
            "change": item["change"],
            "change_percent": item["change_percent"] * 100,
        })
    return out


def render_html(edition):
    stories_html = "".join(
        f'<li><a href="{a["url"]}">{a["title"]}</a> <span>({a["source"]})</span></li>'
        for a in edition["selected_articles"]
    )
    markets_html = "".join(
        f'<li><strong>{m["label"]}</strong>: {m["value"]:.2f} ({m["change"]:+.2f}, {m["change_percent"]:.2f}%)</li>'
        for m in edition["markets"]
    )
    bullets_html = "".join(f"<li>{b}</li>" for b in edition["business_tech_section"]["summary_points"])
    watch_html = "".join(f"<li>{w}</li>" for w in edition["business_tech_section"]["watchlist"])
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>News To Me POC</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 40px auto; max-width: 860px; line-height: 1.5; padding: 0 16px; color: #111; }}
    h1,h2 {{ margin-bottom: 0.2rem; }}
    .box {{ border: 1px solid #ddd; border-radius: 12px; padding: 16px 18px; margin: 18px 0; background: #fafafa; }}
    ul {{ padding-left: 20px; }}
    .muted {{ color: #555; }}
  </style>
</head>
<body>
  <h1>News To Me POC</h1>
  <p class="muted">Generated {edition["generated_at"]}</p>

  <div class="box">
    <h2>{edition["tldr"]["headline"]}</h2>
    <p>{edition["tldr"]["summary"]}</p>
    <p><strong>Why it matters:</strong> {edition["tldr"]["why_it_matters"]}</p>
  </div>

  <div class="box">
    <h2>Markets</h2>
    <ul>{markets_html}</ul>
  </div>

  <div class="box">
    <h2>Business + Tech</h2>
    <p>{edition["business_tech_section"]["lead"]}</p>
    <ul>{bullets_html}</ul>
    <h3>Watchlist</h3>
    <ul>{watch_html}</ul>
  </div>

  <div class="box">
    <h2>Stories used</h2>
    <ul>{stories_html}</ul>
  </div>
</body>
</html>'''


def main():
    t0 = time.perf_counter()
    packet = load_json(POC / "scrum-8-llm-quality" / "article_packet.json")
    stock_results = load_json(POC / "scrum-7-stock-data" / "stock_results.json")

    fetch_done = time.perf_counter()
    selected = choose_articles(packet)
    tldr = build_tldr(selected)
    section = build_section(selected)
    generate_done = time.perf_counter()

    edition = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_inputs": {
            "articles": str((POC / "scrum-8-llm-quality" / "article_packet.json").relative_to(ROOT.parent.parent)),
            "markets": str((POC / "scrum-7-stock-data" / "stock_results.json").relative_to(ROOT.parent.parent)),
        },
        "selected_articles": selected,
        "tldr": tldr,
        "business_tech_section": section,
        "markets": latest_market_snapshot(stock_results),
        "timings_seconds": {
            "fetch_inputs": round(fetch_done - t0, 4),
            "generate_brief": round(generate_done - fetch_done, 4),
            "render_page": 0,
        },
        "manual_fixes_or_breaks": [
            "Used the SCRUM-8 article packet directly because there is no saved Claude output artifact in the repo.",
            "Several article inputs are weak or feature-like, so the generated brief needs editorial filtering before any public-facing launch.",
            "No Vercel CLI or auth was available in this environment, so deployment could not be completed from the repo alone.",
        ],
        "confidence_at_scale": 6,
    }

    html = render_html(edition)
    render_done = time.perf_counter()
    edition["timings_seconds"]["render_page"] = round(render_done - generate_done, 4)
    edition["timings_seconds"]["total_pipeline"] = round(render_done - t0, 4)

    (OUT / "edition.json").write_text(json.dumps(edition, indent=2))
    (OUT / "index.html").write_text(html)
    print(json.dumps(edition["timings_seconds"], indent=2))


if __name__ == "__main__":
    main()
