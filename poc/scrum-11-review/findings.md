# SCRUM-11, Sprint 0 review

## Executive summary
Sprint 0 was directionally successful.

The POCs did not validate a single magical free API that solves intake, summary quality, markets, and delivery by itself. What they did validate is a workable low-cost architecture for an MVP:
- curated RSS as the primary intake backbone
- NewsAPI and newsdata.io as optional supplementary breadth sources, not foundations
- `yfinance` for the daily market snapshot
- a model adapter with the current prompt/schema shape for generation
- Resend for outbound email
- a simple static-output pipeline that already works locally

My recommendation is **Go for Sprint 1, with conditions**.

This is not a clean "everything passed" go. It is a practical go based on the fact that the core path is viable if we keep scope tight and acknowledge the real risks.

## Dependency verdicts

### SCRUM-5, NewsAPI
- Verdict: **Conditional / supplementary only**
- Decision: do not use as the primary source backbone
- Why:
  - US coverage looked usable
  - India category coverage was weak in this run
  - payloads were headline + description + truncated content, not real article bodies
- Best role:
  - fallback breadth source
  - keyword/discovery enrichment when the RSS set is thin

### SCRUM-6, RSS feeds
- Verdict: **Use**
- Decision: RSS should be the primary free intake backbone for the MVP
- Why:
  - best freshness and reliability in the tested set
  - zero direct API cost and no obvious quota pain
  - strong enough breadth when using a curated publisher list
- Important caveat:
  - feeds mostly provide headlines plus short excerpts, not full article bodies

### SCRUM-7, market data
- Verdict: **Use Yahoo Finance, fallback Alpha Vantage**
- Decision:
  - primary: `yfinance`
  - fallback only: Alpha Vantage
- Why:
  - Yahoo returned all 4 required indices cleanly in 3/3 runs
  - Alpha Vantage was quota-sensitive and weaker on exact India index support
- MVP scope call:
  - keep markets simple: S&P 500, NASDAQ, NIFTY 50, SENSEX
  - do not make top gainers/losers a Sprint 1 requirement

### SCRUM-8, LLM generation quality
- Verdict: **Conditional use**
- Decision: proceed with the current prompt/schema shape behind a swappable model adapter
- Why:
  - JSON reliability passed 3/3 for both tested prompt types
  - latency in this environment was trivial
  - editorial quality was limited more by packet quality than by output formatting
- Caveat:
  - exact dollar cost could not be measured in this oauth-backed environment

### SCRUM-9, email delivery
- Verdict: **Use Resend for MVP send path**
- Decision: Resend is acceptable for Sprint 1 outbound delivery
- Why:
  - API send worked immediately
  - quota is comfortably sufficient for one edition per day
- Caveat:
  - production sender domain still needs verification
  - Gmail inbox placement and Apple Mail rendering still need a manual real-mailbox check

### SCRUM-10, end-to-end pipeline spike
- Verdict: **Architecture pass, ops partial pass**
- Decision: keep the file-based pipeline shape for Sprint 1
- Why:
  - local ingest -> generate -> render path already works
  - static output is a good fit for the first version
- Caveat:
  - deployment was not validated because Vercel auth/tooling were unavailable

### SCRUM-12, newsdata.io
- Verdict: **Conditional / supplementary only**
- Decision: use only as a secondary source, especially for India coverage
- Why:
  - better India category coverage than NewsAPI in this test
  - still weak text depth on the free tier
  - free-tier 12-hour delay is a real freshness hit for a morning product

## Invalidated or weakened assumptions

### 1. Aggregator APIs would provide enough article text for strong summaries
Invalidated.

Both NewsAPI and newsdata.io were effectively metadata + short description products in this test. RSS also mostly provided excerpts, not full bodies.

Implication:
- Sprint 1 should assume the first version summarizes from titles + excerpts + tight curation
- richer article-page fetch/cleaning should be treated as a later quality upgrade, not assumed to exist now

### 2. One aggregator could act as the clean primary source
Invalidated.

Neither NewsAPI nor newsdata.io is strong enough on the free tier to be the main backbone without heavy downstream filtering.

Implication:
- use curated publisher RSS as the spine
- use aggregators only to widen recall when needed

### 3. Movers would be easy to add to the markets box
Weakened.

US movers were available from Alpha Vantage but noisy. India movers were not cleanly validated.

Implication:
- ship a simple indices-only market box first

### 4. Deployment validation would be part of the Sprint 0 spike
Partially invalidated.

The local pipeline passed, but a real live URL could not be produced because deploy credentials/tooling were missing.

Implication:
- deployment setup is still a real Sprint 1 task, not a closed question

### 5. Cost would be fully measurable during the LLM POC
Invalidated for this environment.

Token volume was measurable, but direct price accounting was not.

Implication:
- Sprint 1 should preserve model portability and add explicit cost tracking once the production model/API path is chosen

## Recommended Sprint 1 architecture

### Intake
- Primary: curated RSS feeds by section and region
- Secondary: NewsAPI and/or newsdata.io only when we need more candidate stories
- Required downstream steps:
  - dedupe
  - source-quality ranking
  - title/excerpt filtering
  - section-aware scoring

### Generation
- Keep the current JSON-first prompt shape
- Use a model adapter so the generator can be swapped without changing the rest of the pipeline
- Treat packet curation as the main quality lever, not prompt cleverness

### Markets
- Daily snapshot only:
  - S&P 500
  - NASDAQ
  - NIFTY 50
  - SENSEX
- Source: `yfinance`
- Fallback only: Alpha Vantage

### Delivery
- Render static HTML
- Publish via a simple static host once credentials are configured
- Send via Resend after real sender-domain verification

## Top risks going into Sprint 1
1. **Editorial quality risk**
   - weak source packets will produce weak summaries even when the model behaves
2. **Freshness/text-depth risk**
   - free sources are good for discovery, but not for rich article bodies
3. **Deployment readiness risk**
   - live hosting remains unproven in this environment
4. **Email deliverability risk**
   - API send passed, inbox placement still needs a real mailbox check
5. **Unofficial dependency risk**
   - `yfinance` is convenient but unofficial

## Mitigations
- keep Sprint 1 scope small and quality-biased
- prefer fewer, cleaner stories over stuffing sections
- store intermediate artifacts for every run so weak packets are diagnosable
- keep generator and delivery adapters swappable
- add a lightweight fallback plan if `yfinance` breaks

## Alternatives for failed or partial areas
- If RSS excerpt depth proves too thin, add article-page fetch and cleaning as the next major quality investment
- If NewsAPI/newsdata.io add more noise than value, disable them entirely and stay RSS-first
- If Vercel setup is annoying, publish the static output through any simpler static host or even email-first while web publishing catches up
- If Resend inbox placement disappoints, keep Resend for dev and re-evaluate the sender path before broader rollout

## Go / no-go call
**Recommendation: Go to Sprint 1, with conditions.**

Conditions before claiming production readiness:
- real sender domain set up in Resend
- one manual Gmail inbox-placement check
- one Apple Mail rendering check
- deployment credentials/path configured for the static page
- explicit source-ranking and filtering work prioritized early in Sprint 1

## What still needs Mr. Main confirmation
This ticket asked for final go confirmation from the architect/owner before Sprint 1 begins.

My recommendation is:
- **Go** on the MVP architecture
- **Do not** call it launch-ready yet
- **Do** treat source curation and deploy setup as the immediate next work
