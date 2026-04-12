# SCRUM-13 Article Fetcher POC

This POC validates a polite article-page fetcher that visits publisher URLs after RSS/API discovery, extracts the full article text when possible, and preserves graceful fallback when extraction fails.

## Deliverables

- `../../pipeline/fetchers/article_fetcher.py` - reusable fetcher module
- `run_article_fetcher_checks.py` - test harness against real RSS-derived URLs
- `article_fetch_results.json` - per-URL extraction output
- `excerpt_vs_fulltext.json` - side-by-side excerpt versus fetched full text for 3 articles
- `summary.json` - extraction success rate, average text length, and failure rollup
- `findings.md` - recommendation and caveats

## Run

```bash
.venv/bin/python poc/scrum-13-article-fetcher/run_article_fetcher_checks.py
```
