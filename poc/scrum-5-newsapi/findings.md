# SCRUM-5, NewsAPI POC

## Verdict
Supplementary only, not good enough as the primary source for News To Me.

## What I tested
- `top-headlines` with `country=us` and categories `technology`, `business`
- `top-headlines` with `country=in` and categories `technology`, `business`
- `everything` with `q=india`
- `everything` with `q=usa`
- repeat query check for consistency on `top-headlines us technology`

## Article count per query
- `top-headlines country=us category=technology`, totalResults=68, returned=5
- `top-headlines country=us category=business`, totalResults=27, returned=5
- `top-headlines country=in category=technology`, totalResults=0, returned=0
- `top-headlines country=in category=business`, totalResults=0, returned=0
- `everything q=india`, totalResults=20240, returned=5
- `everything q=usa`, totalResults=12321, returned=5

## Body text quality assessment
Observed result: no full article bodies in sampled responses.

Breakdown from returned articles:
- `everything_india`, 5 returned, 5 truncated `content`, 0 full text
- `everything_us`, 5 returned, 5 truncated `content`, 0 full text
- `top_us_business`, 5 returned, 4 truncated `content`, 1 with no usable text fields
- `top_us_technology`, 5 returned, 3 truncated `content`, 1 description-only, 1 with no usable text fields
- India `top-headlines` business and technology returned zero articles in this test

Practical reading: NewsAPI mostly gives headline + description + a truncated content snippet, not the full article body. Some results have even less.

## Coverage assessment
### US
Decent for top-headlines in business and technology. Queries returned live-looking article sets and stable counts across repeat calls.

### India
Weak on `top-headlines` for the tested categories. Both `country=in&category=technology` and `country=in&category=business` returned zero results during this run. `everything q=india` returned many matches, but these are keyword search results, not clean category feeds.

## `everything` vs `top-headlines`
- `everything` gives much larger result sets and is better for broad recall
- `top-headlines` is cleaner for editorial slices when it has data
- for India category coverage, `everything` was materially more useful than `top-headlines`
- downside: `everything` still does not solve the full-text problem

## Rate limit observed
I did not exhaust the daily cap in this run, so this is not a hard empirical upper bound.

Observed behavior:
- repeated requests succeeded without transient failures in this short test
- no rate-limit headers or remaining-quota details were surfaced in the sampled responses
- based on the Jira handoff notes, this needs to be treated as a low free-tier budget and monitored conservatively

## Gotchas
- Free-tier style responses are mostly truncated, not full article text
- India category results were poor in this test
- Some articles had missing `description` and missing `content`
- Source quality is mixed, not just major publications
- `everything` can find a lot, but it is search-driven and will need stronger filtering/deduping before downstream summarization

## Recommendation
Use NewsAPI as a supplementary source, not the primary backbone.

Why:
- US coverage is usable
- India category coverage looked weak in this test
- lack of full text is a real limitation for high-quality summarization
- mixed source quality means extra filtering will be needed anyway

Best role for it:
- supplement RSS and possibly newsdata.io
- use it for breadth and discovery
- do not bet the whole morning-paper pipeline on it alone

## Deliverables in this folder
- `samples/*.json`, raw API responses
- `samples/*.summary.json`, trimmed examples for quick review
- `run_newsapi_checks.py`, reproducible test script
