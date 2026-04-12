# Sprint 0 evidence index

## Child tickets and local deliverables

### SCRUM-5, NewsAPI
- Folder: `../scrum-5-newsapi/`
- Key files:
  - `findings.md`
  - `run_newsapi_checks.py`
  - `samples/*.json`
  - `samples/*.summary.json`
- Verdict: supplementary only

### SCRUM-6, RSS feed validation
- Folder: `../scrum-6-rss/`
- Verdict: use as the MVP intake backbone

### SCRUM-7, stock data
- Folder: `../scrum-7-stock-data/`
- Key files:
  - `findings.md`
  - `run_stock_checks.py`
  - `stock_results.json`
  - `alpha_vantage_manual_checks.json`
- Verdict: use `yfinance`, keep Alpha Vantage as fallback only

### SCRUM-8, LLM quality
- Folder: `../scrum-8-llm-quality/`
- Key files:
  - `findings.md`
  - `run_metrics.json`
  - `llm_abstraction.py`
  - `raw_outputs/`
- Verdict: proceed conditionally with the current schema-first generation shape

### SCRUM-9, Resend delivery
- Folder: `../scrum-9-resend/`
- Key files:
  - `findings.md`
  - `email_template.html`
  - `send_resend_check.py`
  - `evidence/send_response.json`
  - `manual_inbox_check.md`
- Verdict: use for MVP send path, but real mailbox checks still required

### SCRUM-10, pipeline spike
- Folder: `../scrum-10-pipeline/`
- Key files:
  - `findings.md`
  - `README.md`
  - `deploy_notes.md`
  - `output/edition.json`
  - `output/index.html`
- Verdict: local architecture pass, live deploy still pending credentials

### SCRUM-11, Sprint 0 review
- Folder: `../scrum-11-review/`
- Key files:
  - `findings.md`
  - `architecture-decisions.md`
- Verdict: Go for Sprint 1, with conditions

### SCRUM-12, newsdata.io
- Folder: `../scrum-12-newsdata/`
- Key files:
  - `findings.md`
  - `samples/*.json`
  - `samples/*.summary.json`
- Verdict: supplementary only, but stronger than NewsAPI for India coverage in this test

## Net outcome
### Passed cleanly enough for Sprint 1
- RSS-first intake
- `yfinance` for the 4-index market snapshot
- static-output pipeline shape
- Resend API send path

### Passed conditionally
- LLM generation cost/quality
- NewsAPI
- newsdata.io
- deployment workflow

### Still needs explicit owner sign-off
- final Sprint 1 go confirmation
- sender-domain verification plus inbox/render checks
- deployment path/tooling choice
