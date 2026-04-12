# SCRUM-8 findings

## Verdict

**Conditional pass for MVP prototyping.**

The prompt shape is workable and the model was reliably returning parseable JSON for both the TL;DR box and a Business + Tech section summary. The bigger issue is not JSON reliability, it is source quality and observability: the article packet was thin and mixed hard news with rumor / feature-style items, and this environment did not expose direct per-token billing.

## Model tested

- **Model:** `openai-codex/gpt-5.4`
- **Access path:** OpenClaw subagent sessions over oauth
- **Reason for choice:** this was the live model available in the agent environment during the POC run
- **Pricing visibility:** exact per-token pricing was **not exposed** in `session_status` for this oauth-backed environment, so a true dollar-cost measurement was not possible from inside this run

## What I tested

I ran the supplied prompts against the same 5-article packet:

- 3 TL;DR runs
- 3 Business + Tech summary runs

Artifacts:

- `article_packet.json`
- `tldr_prompt.txt`
- `news_summary_prompt.txt`
- `raw_outputs/`
- `run_metrics.json`
- `llm_abstraction.py`

## JSON reliability

### TL;DR prompt

- Valid JSON: **3/3**
- Schema adherence: **3/3**
- Repeated story selection: inflation + OpenAI incident + Anthropic Mythos + foldable iPhone in all runs

### Business + Tech summary prompt

- Valid JSON: **3/3**
- Schema adherence: **3/3**
- Repeated framing: inflation / energy shock first, then AI safety + security, then Apple/Xbox as secondary items

## Latency and token usage

Measured from subagent session timestamps and `session_status` token counters.

### TL;DR runs

| Run | Input tokens | Output tokens | Latency |
| --- | ---: | ---: | ---: |
| 1 | 7.4k | 242 | 38 ms |
| 2 | 7.4k | 257 | 30 ms |
| 3 | 7.4k | 264 | 34 ms |

### Summary runs

| Run | Input tokens | Output tokens | Latency |
| --- | ---: | ---: | ---: |
| 1 | 7.3k | 272 | 25 ms |
| 2 | 7.3k | 237 | 23 ms |
| 3 | 7.3k | 248 | 25 ms |

### Estimated token cost envelope

Because billing was not exposed for this oauth environment, I could only estimate token volume, not exact spend.

Approximate per-edition token budget if we extrapolate from this POC shape:

- 1 TL;DR call: about **7.7k input / 255 output**
- 7 section-style calls: about **51.1k input / 1.74k output** if article packets are similar in size
- Full edition rough total: about **58.8k input / 2.0k output**

That is directionally acceptable for an MVP if we later swap to a paid API model with known pricing, but the real driver will be **how large each section packet becomes after curation**.

## Quality assessment

## What worked

- Output was consistently structured and parseable.
- Tone was mostly crisp and newspaper-ish, not chatty.
- The model usually anchored on the strongest hard-news item first.
- Watchlists were concise and useful.

## What was weak

- “Why it matters” stayed competent but generic.
- The model kept including weaker packet items because the source packet itself was weak.
- The prompt did not fully suppress rumor-ish or feature-y items when hard-news inventory was thin.
- The runs were stable, but **stable on mediocre input still gives mediocre output**.

## Prompt adjustment recommendations

1. Add a stronger instruction to **downrank rumor, profile, and feature items** when at least two clear hard-news items exist.
2. Add an explicit rule to treat **Reuters / WSJ-level hard news as anchor stories** when present.
3. Require a short confidence note or excluded-story list in non-MVP diagnostics, so weak packet quality is visible upstream.
4. Keep the JSON schema simple. The current shape is already reliable enough.

## Recommendation

Use this prompt-and-schema shape for Sprint 1, but do **not** treat this as proof that generation quality is solved.

My read is:

- **JSON reliability:** pass
- **Latency in this environment:** pass
- **Cost measurement:** incomplete because billing was hidden
- **Editorial quality:** conditional pass, limited mainly by source-packet quality

## Go / no-go

**Go, with conditions:**

- proceed with a swappable model adapter
- keep packet curation as the main quality lever
- add real API-based cost measurement later when using a priced production model
- do not overfit prompts before the intake layer improves
