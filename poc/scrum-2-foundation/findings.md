# SCRUM-2, Sprint 1 foundation spike

## Verdict
Proceed. Sprint 0 reduced enough uncertainty to start building the real fetch foundation, but the first implementation should stay deliberately narrow and quality-biased.

## What this package does
This spike converts Sprint 0 conclusions into a buildable Sprint 1 starting point:
- RSS-first source registry
- SQLite schema for run tracking and deduplicated article storage
- runnable fetch orchestrator spike that stores live feed results
- explicit boundaries so aggregators and article-page extraction can be added later without ripping up the core

## Why this shape
Sprint 0 made a few things clear:
- RSS is the strongest free intake backbone
- aggregator APIs are useful only as optional enrichment
- title + excerpt is the default input shape for now
- the system needs good storage and run visibility before it needs prompt cleverness

That means Sprint 1 should start by making article collection reliable, inspectable, and easy to evolve.

## Design calls in this spike
### 1. RSS-first registry
Sources are declared in `source_registry.json` with:
- id
- kind
- region
- section
- tier
- url

This is intentionally simple enough to edit by hand while still being structured enough for a fetch orchestrator.

### 2. SQLite before anything more complex
SQLite is the right first storage layer here.

Why:
- trivial local setup
- good enough for one daily paper pipeline
- easy to inspect and back up
- supports dedupe and downstream filtering without infra overhead

### 3. Dedupe at ingest time
The spike deduplicates using a stable key derived from canonical URL when possible, otherwise normalized title.

This is not the final dedupe logic, but it is the right first line of defense.

### 4. Run-level observability
Every run records:
- start/finish timestamps
- status
- counts for fetched, inserted, duplicate items

That matters because weak editions will be easier to diagnose if intake runs leave artifacts behind.

## Result from the spike run
One local run of `fetch_orchestrator_spike.py` completed successfully and wrote:
- `sample_output/news_to_me.db`
- `sample_output/run_summary.json`
- `sample_output/section_counts.json`
- `sample_output/latest_articles.json`

Measured result from that run:
- sources queried: 9
- fetched rows: 449
- inserted rows: 449
- duplicate rows: 0 on the first pass
- stored sections covered: India top, India business, world top, US top, US business, US technology

This is enough to unblock the next build steps:
- ranking
- section assembly
- optional aggregator adapters
- optional article-page extraction

## Recommendation for the next implementation step
After this foundation package, the next best move is:
1. promote the spike into a real project module
2. add ranking/filtering rules from the Sprint 0 review
3. only then add optional NewsAPI/newsdata adapters behind feature flags

## Caveats
- RSS payload depth is still excerpt-level, not full text
- this spike does not yet fetch article pages
- the dedupe strategy should eventually add fuzzy title matching and outlet-aware canonicalization
- no scheduler is included here yet

## Bottom line
Sprint 1 should begin with reliable collection and storage, not with bigger prompts or more source sprawl.

This package gives the project a clean first foundation for that.
