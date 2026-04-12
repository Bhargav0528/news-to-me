# SCRUM-3 generate + publish spike

This package turns the saved Sprint 1 intake artifacts into a full, readable 7-section edition.

## Run
```bash
cd /home/bbv/.openclaw/workspace/peeohsee-1/projects/news-to-me/poc/scrum-3-generate-publish
python3 run_generate_publish_spike.py
```

## Inputs
- `../scrum-2-foundation/sample_output/news_to_me.db`
- `../scrum-7-stock-data/stock_results.json`

## Outputs
- `sample_output/edition.json`
- `sample_output/diagnostics.json`
- `sample_output/index.html`

## Scope
This proves section assembly and static-page rendering from real saved inputs.
It does not yet prove production deployment, final ranking quality, or full LLM-written copy quality.
