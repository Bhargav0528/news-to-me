# SCRUM-2 foundation package

This folder turns the Sprint 0 POC conclusions into an implementation-ready Sprint 1 foundation spike.

## Deliverables
- `findings.md` - what Sprint 1 should build first, and why
- `source_registry.json` - initial RSS-first source configuration
- `schema.sql` - SQLite schema for runs, sources, and deduplicated articles
- `fetch_orchestrator_spike.py` - runnable spike that fetches RSS feeds and stores deduplicated articles in SQLite
- `sample_output/` - artifacts from one local run

## How to run
```bash
cd /home/bbv/.openclaw/workspace/peeohsee-1/projects/news-to-me/poc/scrum-2-foundation
python3 fetch_orchestrator_spike.py
```

By default it writes:
- `sample_output/news_to_me.db`
- `sample_output/run_summary.json`

## Scope
This is a foundation spike, not the final production fetch layer.

It deliberately proves these things first:
1. the RSS-first source registry shape
2. the SQLite storage model
3. a simple dedupe strategy that works across feeds
4. the basic run-recording and source-attribution pattern

It does **not** yet include:
- article-page extraction
- aggregator fallbacks
- scheduling
- ranking/scoring
- section assembly
