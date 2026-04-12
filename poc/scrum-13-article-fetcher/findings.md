# Findings

## Verdict

`trafilatura` is the best primary extractor for the News To Me pipeline.

Why:
- It handled 6 of the 7 successful extractions directly.
- It produced clean long-form text across The Hindu, BusinessLine, BBC, CNBC, TechCrunch, Ars Technica, and Indian Express.
- It behaved well on normal article pages without site-specific tuning.

`readability-lxml` is worth keeping as a fallback.
- It rescued one The Hindu article that did not meet the minimum threshold through `trafilatura` alone.
- The fallback cost is low once the HTML is already fetched.

## Measured result

- Tested URLs: 10
- Successful full-text extractions: 7
- Failures: 3
- Success rate: 70%
- Average extracted text length on successes: 4,539 characters

## What failed

- `nytimes.com` returned HTTP 403 in this run, so the fetcher correctly fell back instead of fabricating text.
- `marketwatch.com` returned HTTP 401 in this run.
- `npr.org` timed out on this sample URL.

These are acceptable pipeline failures as long as the article record keeps the RSS excerpt and the system moves on.

## Recommendation for implementation

Use this fetch order inside the real pipeline:
1. HTTP GET article page with a polite User-Agent
2. Try `trafilatura`
3. Fall back to `readability-lxml`
4. If both fail, keep the original RSS/API excerpt and mark fetch status as failed

## Notes for Sprint 1 follow-through

- Keep the 1-2 second inter-request delay. The current module uses `1.2s` by default.
- Persist `full_text`, `full_text_length`, `fetch_status`, `fetch_method`, and `fetch_error` in SQLite.
- Expect some publisher blocks and timeouts. This is normal, not a reason to stop the pipeline.
- If coverage needs to climb above ~70% on mixed public URLs, the next improvement is retry logic plus site-specific handling for stubborn publishers.
