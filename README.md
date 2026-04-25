# News To Me — Pipeline

## Two-stage architecture

The pipeline is split into two independent stages so each can run with the appropriate timeout budget:

### Stage 1 — `ingest` (fast, ~2–5 min)

Fetches all RSS feeds, enriches articles with full-text extraction, deduplicates, and persists to SQLite.

```bash
python3 -m pipeline.ingest                    # full ingest
python3 -m pipeline.ingest --article-limit 50 # dev: limit articles
python3 -m pipeline.ingest -v                # verbose logging
```

**Safe to run anywhere** — completes well under typical exec timeout limits.

### Stage 2 — `generate` (slow, ~10–15 min)

Reads the most recent ingest data from SQLite, runs all LLM section generators, and writes `edition.json`.

```bash
python3 -m pipeline.generate                    # assemble edition + send email
python3 -m pipeline.generate --deploy           # also deploy to Vercel
python3 -m pipeline.generate --no-email         # skip email (dev/debug)
python3 -m pipeline.generate -v                 # verbose logging
```

**Needs a machine with no short exec timeout.** The GitHub Actions runner (Sprint 3) has a 6-hour job timeout — plenty of budget.

### Dev convenience — `main.py`

Runs ingest then generate sequentially in one process. **For local dev only.**

```bash
python3 -m pipeline.main --deploy --send-email  # full pipeline (dev)
python3 -m pipeline.main --skip-ingest           # skip ingest, use existing DB
```

> ⚠️ **WARNING:** `main.py` may be SIGKILL'd by execution environments with short timeouts. Use the two-stage split above for any automated/scheduled runs.

## Intermediate artifacts

| File | Stage | Description |
|------|-------|-------------|
| `data/news_to_me.db` | After ingest | SQLite DB with raw articles |
| `data/pipeline_status.json` | During any run | Live status (which step is running, last completed step). See [Status file](#status-file) below. |
| `data/edition.json` | After generate | The assembled edition JSON |
| `web/public/data/edition.json` | After generate | Symlink/copy for the web frontend |
| `data/email_preview.json` | After generate | Email preview (also written before send) |

## Status file

During a run, `data/pipeline_status.json` tracks exactly where the pipeline is:

```json
{
  "run_id": "2026-04-26T15:00:00Z",
  "stage": "generate",
  "current_step": "generating growth section",
  "steps_completed": ["ingest", "tldr", "news_bangalore", "news_karnataka", "news_india", "news_us", "news_world", "biztech"],
  "steps_remaining": ["growth", "knowledge", "fun"],
  "started_at": "2026-04-26T15:00:00Z",
  "updated_at": "2026-04-26T15:08:22Z"
}
```

**On success:** `stage` becomes `"completed"`.
**On crash:** the file shows exactly which step was in progress when it died.

This file is in `.gitignore` — it is never committed.

## Git commit behavior

`generate.py` automatically commits `data/edition.json` and `web/public/data/edition.json` to git **only on success**, after the LLM assembly is complete and `edition.json` is written. If LLM assembly fails or is killed, no commit happens and no email is sent.

## Automated scheduling (cron)

A daily cron job runs the pipeline automatically every morning. This is managed via OpenClaw's built-in scheduler, not cron(8).

**Current schedule:** `news-to-me daily` — every day at **7:00 AM Pacific (America/Los_Angeles)**

To view, manage, or remove the cron job:

```bash
openclaw cron list                  # see all cron jobs
openclaw cron runs --id <jobId>     # see run history
openclaw cron run <jobId>           # force-run now
openclaw cron remove <jobId>       # delete a job
```


To recreate the daily cron job:

```bash
openclaw cron add \
  --name "news-to-me daily" \
  --cron "0 7 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Run the News To Me daily pipeline end-to-end.\n\nWorking directory: /home/bbv/.openclaw/workspace/peeohsee-1/projects/news-to-me\n\nSteps:\n1. Run: .venv/bin/python -m pipeline.ingest -v\n2. Run: .venv/bin/python -m pipeline.generate --deploy -v\n3. Report results: ingest summary, status file stage, edition sections populated, deployed URL if any." \
  --announce \
  --channel telegram \
  --to 8450368729
```

**How it works:**
- Runs in an **isolated session** — does not require Becky to be online
- Executes `.venv/bin/python -m pipeline.ingest` then `.venv/bin/python -m pipeline.generate --deploy` sequentially
- On success: announces a summary to Mr. Main's Telegram DMs (8450368729)
- On failure: announces the error and the last status file contents
- Stored at `~/.openclaw/cron/jobs.json` — persists across OpenClaw restarts

## Adding new pipeline stages

The status file tracks steps by name. To add a new generate step:

1. Add the step name to `GENERATE_STEPS` in `pipeline/status.py`
2. Call `status.set_step("my_new_step")` at the start of the step in `pipeline/generate.py`
