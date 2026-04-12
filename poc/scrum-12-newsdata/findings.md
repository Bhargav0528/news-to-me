# SCRUM-12, newsdata.io POC

## Verdict
Supplementary only. Better breadth than NewsAPI for India, but still not strong enough to be the primary source for a high-quality daily paper on the free tier.

## What I tested
- `latest` with `country=in&category=politics`
- `latest` with `country=us&category=technology`
- `latest` with `country=in&category=business`
- `latest` with `country=us&category=business`
- `latest` with search query `q=bangalore`

## Sample response coverage
- `latest_in_politics`, totalResults=7851, returned=10
- `latest_in_business`, totalResults=7275, returned=10
- `latest_us_technology`, totalResults=6466, returned=10
- `latest_us_business`, totalResults=23912, returned=10
- `search_bangalore`, totalResults=247, returned=10

## Content quality
The key limitation showed up immediately: sampled results did not contain meaningful full article content.

Observed across all five sample queries:
- every returned item had tiny `content` fields, about 28 characters long in this run
- descriptions were present most of the time and were materially more useful than `content`
- this means the free-tier payload is effectively title + metadata + short description, not article body text

Practical conclusion: the excerpt is sometimes enough for rough summarization, but not enough to trust for deeper or more nuanced summary generation.

## India coverage vs NewsAPI
Compared with the earlier NewsAPI POC:
- newsdata.io returned populated India category queries immediately
- NewsAPI returned 0 results for the tested India `top-headlines` business and technology queries
- so for India category coverage, newsdata.io looked better in this test

## Quality and source noise
The response quality is mixed.

Observed issues:
- category mismatch and noisy classification, especially in US business/technology where obviously unrelated sports-style articles appeared
- duplicate or near-duplicate stories across multiple outlets
- source quality is broad, but consistency is not strong enough to skip downstream filtering

## 12-hour delay
Based on the ticket notes, the free tier is delayed by 12 hours.

Verdict on the delay:
- for a 5 AM "morning paper", 12-hour lag is a real drawback
- it may still be acceptable for evergreen-ish sections or as a backup source
- it is not ideal if freshness is a core product promise

## Recommendation
Use newsdata.io as a supplementary source, likely stronger than NewsAPI for India coverage, but still not good enough as the sole primary source on the free tier.

Recommended role:
- use it to improve India coverage and broaden the candidate pool
- pair it with RSS or direct publisher feeds for fresher and richer text
- assume dedupe, source filtering, and possibly article-page scraping will still be required

## Deliverables in this folder
- `samples/*.json`, raw API responses
- `samples/*.summary.json`, trimmed examples for quick review

## Bottom line
- India coverage, better than NewsAPI in this test
- article text quality, still weak
- freshness, meaningfully constrained by free-tier delay
- final recommendation, supplementary source, not primary
