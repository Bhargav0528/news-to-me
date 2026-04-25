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

## Cron runbook

**Job:** `news-to-me daily` | **ID:** `1c5fbd54-26fb-40ad-9567-5b6e177dc1df` | **Schedule:** 7:00 AM Pacific daily

### Where the cron is installed

```bash
# View all cron jobs
openclaw cron list

# View run history (last 20 runs)
openclaw cron runs --id 1c5fbd54-26fb-40ad-9567-5b6e177dc1df --limit 20

# View detailed run log
openclaw cron runs --id 1c5fbd54-26fb-40ad-9567-5b6e177dc1df --limit 1 --verbose

# Force-run now (for testing)
openclaw cron run 1c5fbd54-26fb-40ad-9567-5b6e177dc1df

# Remove the job
openclaw cron remove 1c5fbd54-26fb-40ad-9567-5b6e177dc1df
```

Cron job config lives at: `~/.openclaw/cron/jobs.json`

### Secrets / environment variables

| Secret | Location | Purpose |
|--------|----------|---------|
| `.env` file | `/home/bbv/.openclaw/workspace/peeohsee-1/projects/news-to-me/.env` | LLM API keys, Jira creds, Vercel auth |
| Vercel CLI auth | `~/.local/share/com.vercel.cli/auth.json` | Vercel deploys via CLI |
| OpenClaw config | `~/.openclaw/openclaw.json` | Gateway, channels, auth |

**To view current secrets:**
```bash
cat /home/bbv/.openclaw/workspace/peeohsee-1/projects/news-to-me/.env
```

**To update secrets:** edit the `.env` file and restart OpenClaw gateway:
```bash
systemctl --user restart openclaw-gateway  # if using systemd service
openclaw gateway restart                   # or via CLI
```

### Where logs are written

| Log type | Location |
|----------|----------|
| OpenClaw gateway logs | `/tmp/openclaw/openclaw-YYYY-MM-DD.log` |
| Pipeline output | stdout of the isolated cron session (viewable via `openclaw cron runs --verbose`) |
| `data/pipeline_status.json` | `/home/bbv/.openclaw/workspace/peeohsee-1/projects/news-to-me/data/pipeline_status.json` |
| Vercel deploy output | `vercel --prod` stdout captured in cron run log |

```bash
# Tail recent gateway logs
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log

# View pipeline status mid-run
cat /home/bbv/.openclaw/workspace/peeohsee-1/projects/news-to-me/data/pipeline_status.json
```

### What time it fires

**7:00 AM Pacific (America/Los_Angeles), every day.**

`openclaw cron list` shows `next` and `last` columns. Next run is shown as epoch ms.

### What to do when it doesn't fire

**Step 1 — Check the status:**
```bash
openclaw cron runs --id 1c5fbd54-26fb-40ad-9567-5b6e177dc1df --limit 5
```

**Step 2 — Check the pipeline status file:**
```bash
cat /home/bbv/.openclaw/workspace/peeohsee-1/projects/news-to-me/data/pipeline_status.json
```

**Step 3 — Run manually:**
```bash
cd /home/bbv/.openclaw/workspace/peeohsee-1/projects/news-to-me

# Stage 1: ingest (~5 min)
.venv/bin/python -m pipeline.ingest -v

# Stage 2: generate + deploy + email (~10-15 min)
.venv/bin/python -m pipeline.generate --deploy -v
```

**Step 4 — Verify website and email:**
- Website: `https://web-sand-two-88.vercel.app` should show today's date
- Email: check inbox at `bhargavbangalorevmurthy@gmail.com`

**Step 5 — If cron is still failing, check:**
- Is the machine (obsidian/Raspberry Pi) online?
- Is OpenClaw gateway running? (`openclaw gateway status`)
- Is the cron job still there? (`openclaw cron list`)
- Is the `.env` file present and valid?

### How to take over if Becky is unavailable

**Requirements:**
- Access to the machine `obsidian` (Raspberry Pi 5, Linux, user `bbv`)
- OpenClaw installed and configured
- The `.env` file at the path above

**Steps to recreate the cron on a new machine:**
```bash
# 1. Install OpenClaw
npm install -g openclaw

# 2. Configure channels (Telegram, etc.) — see OpenClaw docs

# 3. Create the cron job
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

**Vercel CLI auth:** run `vercel login` and `vercel --yes --prod` once manually to authenticate.

### Pipeline failure modes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Email fires but website shows old content | `web/public/data/edition.json` not updated, Vercel not triggered | Run `vercel --yes --prod` manually from `web/` dir |
| Email not sent | AgentMail API failure or edition.json incomplete | Check `data/pipeline_status.json`, re-run `pipeline.generate` |
| Ingest step fails | RSS feed down or network issue | Re-run `pipeline.ingest`, check RSS feed URLs |
| LLM section fails | API key issue or model outage | Check `.env` OPENAI_API_KEY / ANTHROPIC_API_KEY |
| Cron not firing at all | OpenClaw gateway down or cron job missing | `openclaw gateway status` + `openclaw cron list` |

## Adding new pipeline stages

The status file tracks steps by name. To add a new generate step:

1. Add the step name to `GENERATE_STEPS` in `pipeline/status.py`
2. Call `status.set_step("my_new_step")` at the start of the step in `pipeline/generate.py`
