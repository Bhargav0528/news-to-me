# SCRUM-6, RSS feed validation POC

## Verdict
RSS should be the primary free backbone for News To Me, but only as a discovery and excerpt layer.

It is strong on freshness, feed reliability, and zero-cost access. The catch is that most feeds do **not** include full article bodies, only headlines plus short descriptions or excerpts. That means RSS alone is not enough for deeper summarization unless we are comfortable summarizing from excerpts or add article-page fetching later.

## What I tested
I validated 10 candidate feeds across India, US, world, business, markets, and tech:

1. The Hindu, India / General
2. Indian Express India, India / National
3. The Hindu BusinessLine, India / Business
4. BBC World, World
5. NPR World, World
6. New York Times Home, US / General
7. CNBC Top News, US / Business
8. MarketWatch Top Stories, US / Markets
9. TechCrunch, Tech
10. Ars Technica, Tech

For each feed I checked:
- whether it fetches cleanly and parses reliably
- whether entries contain full article text, excerpts, or headline-only metadata
- how many sampled items were published in the last 24 hours
- how fresh the newest item is
- whether the feed looks usable as part of a daily paper pipeline

## Summary table

- **The Hindu**
  - Freshness: newest item about 0.2h old
  - 24h volume in sampled entries: 15
  - Content shape: mostly headline + short excerpt, one headline-only item
  - Reliability: good
  - Take: strong India general source, but excerpt quality is inconsistent

- **Indian Express India**
  - Freshness: newest item about 0.22h old
  - 24h volume in sampled entries: 15
  - Content shape: headline/link only in all sampled entries
  - Reliability: good
  - Take: very fresh, but poor for direct summarization without fetching the article page

- **The Hindu BusinessLine**
  - Freshness: newest item about 0.08h old
  - 24h volume in sampled entries: 15
  - Content shape: headline + short excerpt
  - Reliability: good
  - Take: one of the better India business feeds, definitely worth keeping

- **BBC World**
  - Freshness: newest item about 0.21h old
  - 24h volume in sampled entries: 14
  - Content shape: headline + short excerpt
  - Reliability: good
  - Take: solid world-news backbone feed

- **NPR World**
  - Freshness: newest item about 10.87h old
  - 24h volume in sampled entries: 9
  - Content shape: short excerpt only
  - Reliability: good
  - Take: useful secondary world source, but not especially high-volume or ultra-fresh

- **NYT Home**
  - Freshness: newest item about 0.8h old
  - 24h volume in sampled entries: 14
  - Content shape: headline + short excerpt
  - Reliability: good
  - Take: strong US general source

- **CNBC Top News**
  - Freshness: newest item about 5.18h old
  - 24h volume in sampled entries: 8
  - Content shape: headline + short excerpt
  - Reliability: good
  - Take: decent business feed, but freshness is weaker than the best feeds

- **MarketWatch Top Stories**
  - Freshness: newest item about 13.03h old
  - 24h volume in sampled entries: 10
  - Content shape: headline + short excerpt
  - Reliability: good
  - Take: usable for markets color, but too feature-heavy for a core hard-news slot

- **TechCrunch**
  - Freshness: newest item about 4.95h old
  - 24h volume in sampled entries: 5
  - Content shape: headline + short excerpt
  - Reliability: good
  - Take: good startup/consumer-tech feed, lower volume than a general news backbone

- **Ars Technica**
  - Freshness: newest item about 20.69h old
  - 24h volume in sampled entries: 1
  - Content shape: materially better excerpts, sometimes long excerpt, but still not full article text
  - Reliability: good
  - Take: best text richness in this test, but low publishing frequency makes it a secondary source

## Full text vs excerpt finding
This was the key result.

Observed behavior across the 10 feeds:
- **0 feeds** consistently returned full article bodies in RSS
- most feeds returned **headline + short excerpt**
- **Indian Express India** was effectively **headline/link only** in the sampled entries
- **Ars Technica** stood out as the richest feed, with longer excerpts around 100-235 words, but still not complete article text

Practical conclusion: RSS is excellent for discovery, metadata, and lightweight summaries, but not sufficient as a full-text source if we want consistently strong TLDR generation from raw feed payloads alone.

## Reliability and freshness
The good news is that RSS itself looked strong.

Observed across this run:
- all 10 feeds returned HTTP 200 and parsed successfully
- all 10 looked stable enough to use operationally
- the freshest feeds were The Hindu BusinessLine, The Hindu, Indian Express, and BBC World
- some otherwise useful feeds were noticeably less fresh, especially NPR World, MarketWatch, and Ars Technica

So the operational risk is not rate limits or outages. The real limitation is payload depth.

## Recommended feed set for the POC
If I were wiring the first RSS backbone today, I would keep these as the default set:

### Primary set
- The Hindu
- The Hindu BusinessLine
- BBC World
- NYT Home
- TechCrunch

### Secondary / optional enrichment
- Indian Express India
- NPR World
- CNBC Top News
- Ars Technica

### Use sparingly
- MarketWatch Top Stories
  - useful, but it tilts toward service/features and is not as hard-news-focused as the others

## Recommendation
Use RSS as the **primary free intake backbone**, but design the system around what RSS actually provides:
- title
- link
- source
- timestamp
- short excerpt when available

That means:
1. **Yes, use RSS heavily** for breadth, freshness, and cost control
2. **No, do not assume full article text is available** in the feed itself
3. plan for one of these next:
   - summarize from excerpt-level inputs for the first version, or
   - fetch and clean article pages for a richer text layer later
4. mix publisher feeds rather than relying on one aggregator, because source quality is meaningfully better this way

## Bottom line
RSS passed the POC as the best free backbone so far.

Why it passed:
- free and effectively unlimited
- reliable
- fresh
- broad enough to cover key sections with a curated feed list

Why it is not enough on its own:
- almost no full article text in-feed
- excerpt depth varies a lot by publisher
- some feeds are headline-only and need article-page fetch as a second step

## Deliverables in this folder
- `run_rss_checks.py`, reproducible validation script
- `rss_results.json`, consolidated machine-readable results
- `samples/*.xml`, raw feed payloads
- `samples/*.summary.json`, per-feed summaries for quick review
