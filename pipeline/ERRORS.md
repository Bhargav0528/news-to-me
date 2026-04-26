# Pipeline Error Reference

This document lists every failure mode in the News To Me pipeline, the policy for each, and recovery instructions.

## Failure Mode Index

| Mode | Severity | Policy | Recover by |
|------|----------|--------|------------|
| RSS feed down | WARN | Skip feed, continue | Re-run ingest later |
| Article fetch timeout | WARN | Mark failed, continue | Re-run ingest |
| LLM call fails | RETRY | 3x exponential backoff | Auto |
| HTTP fetch fails | RETRY | 2x with 5s backoff | Auto |
| Git push fails | RETRY | 2x with 10s backoff | Auto |
| Vercel CLI fails | RETRY | 2x with 10s backoff | Auto |
| AgentMail API fails | RETRY | 3x with 5s backoff | Auto |
| Section generator fails | DEGRADE | Log + sentinel, continue | Next successful run |
| ALL sections fail | ABORT | Alert admin, exit 1 | Manual |
| Edition validation fails | ABORT | Log broken edition, alert admin, exit 1 | Manual |
| DB empty | ABORT | Clear error message, exit 1 | Run ingest first |
| No network | ABORT | Log + alert, exit 1 | Manual |

---

## Failure Modes

### 1. RSS / HTTP fetcher failures

**What:** An RSS feed or HTTP article fetch returns an error or times out.

**Policy:** Per-feed, per-article failures are caught and logged as WARN. The pipeline continues with the remaining articles. No edition is generated if zero articles are fetched successfully.

**Retry:** HTTP calls use the `http_retry` decorator (2 retries, 5s backoff).

**Recovery:** Re-run ingest. If the feed is permanently down, remove from source registry.

---

### 2. LLM call failures

**What:** OpenAI or Anthropic API returns an error (rate limit, timeout, auth failure).

**Policy:** Each LLM call uses `llm_retry` (3 retries, exponential backoff starting at 2s). If all retries fail, the section generator marks itself as failed.

**Retry:** Decorator `pipeline/utils/retry.py` with `max_attempts=3`, `base_delay=2.0`, `exponential=True`.

**Recovery:** Auto on rate-limit errors (backoff clears the queue). Manual check if API key is wrong or model is down.

---

### 3. Git push failure

**What:** `git push origin main` fails (network issue, auth revoked, empty commit).

**Policy:** 2 retries with 10s backoff. If still failing, log WARNING and continue — the edition.json is already on disk and will be in the next commit.

**Recovery:** Manual `git push origin main` once resolved.

---

### 4. Vercel deploy failure

**What:** `vercel --prod` returns non-zero exit code or URL cannot be parsed.

**Policy:** 2 retries with 10s backoff. If still failing, log ERROR and abort (do NOT send email with a stale URL).

**Recovery:** Run `vercel --prod` manually from the `web/` directory once Vercel auth is refreshed.

---

### 5. AgentMail API failure

**What:** AgentMail `messages.send` API returns non-200.

**Policy:** 3 retries with 5s backoff. If still failing, log ERROR and abort — do not silently skip email.

**Recovery:** Check `AGENTMAIL_API_KEY` in `.env`. Verify inbox exists at console.agentmail.to.

---

### 6. Section-level graceful degradation

**What:** Any single section generator (news region, biztech, growth, knowledge, fun) throws an exception after all retries are exhausted.

**Policy:** 
1. Log ERROR with the full exception.
2. Insert sentinel value in `edition.json` for that section:
   ```json
   {
     "_error": "generation_failed",
     "failed_section": "growth",
     "timestamp": "2026-04-25T14:00:00Z",
     "message": "OpenAI API rate limit exceeded after 3 retries"
   }
   ```
3. Continue to the next section. The frontend renders a placeholder: `"⚠️ This section couldn't be generated today. The rest of your paper is below."`
4. Do NOT abort the pipeline.

**Recovery:** Next successful run replaces the sentinel with real content.

---

### 7. ALL sections fail

**What:** Every section generator fails (e.g., API credentials are wrong, no data in DB).

**Policy:** Pipeline aborts. Log ERROR. Send admin alert (email to admin address). Write broken edition to `data/broken_editions/edition_YYYY-MM-DD_HHMMSS_broken.json`. Exit code 1.

**Recovery:** Fix root cause (check API keys, run ingest first). The broken edition files are in `data/broken_editions/` for debugging.

---

### 8. Edition validation failure

**What:** `edition.json` does not pass schema validation before commit.

**Policy:** Pipeline aborts. Log ERROR listing validation failures. Write broken edition to `data/broken_editions/`. Send admin alert. Exit 1. Do NOT commit or deploy broken content.

**Schema checks:**
- All 7 top-level keys present: `date`, `edition_number`, `generated_at`, `tldr`, `news`, `biztech`, `growth`, `knowledge`, `fun`
- `date` is a valid ISO date string
- `tldr` is a list with at least 1 item
- `news` has all 5 regions; each region is a list
- `biztech.articles` is a list
- URLs in `source_url` fields are well-formed
- No section is `null` or completely empty (unless marked `_error: "generation_failed"`)

---

### 9. Database empty

**What:** `raw_articles` table has 0 rows when generate starts.

**Policy:** Pipeline aborts immediately with clear message: "Run `python3 -m pipeline.ingest` first." Exit 1.

**Recovery:** Run ingest first.

---

### 10. No network connectivity

**What:** Machine is offline, all HTTP calls fail.

**Policy:** Pipeline aborts. Log ERROR. Send admin alert. Exit 1.

---

## Admin Alerting

On catastrophic failure (modes 7, 8, 10), send an alert to the admin address using AgentMail:

```python
admin_config = EmailConfig(
    recipient=os.getenv("ADMIN_EMAIL", "bhargavbangalorevmurthy@gmail.com"),
    # subject prefixed with "[ALERT] "
)
```

Subject: `[ALERT] News To Me pipeline failed: {reason}`
Body: `Pipeline aborted on {date}. {reason}. Check data/broken_editions/ for details.`

---

## Log Levels

| Level | When to use |
|-------|-------------|
| INFO | Normal progress (ingest started, section started, email sent) |
| WARN | Partial failures (one feed down, one article failed, one retry succeeded) |
| ERROR | Abort-worthy failures (API key wrong, all retries exhausted, validation failed) |
| DEBUG | Detailed tracing (LLM call input/output, HTTP response bodies) |

Log format: `%(asctime)s %(levelname)s %(name)s: %(message)s`