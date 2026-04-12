# Sprint 1 architecture decisions after Sprint 0 POCs

## Decision 1: Intake should be RSS-first, not aggregator-first
**Status:** accepted

Use curated publisher RSS feeds as the primary intake layer.

Why:
- best freshness and reliability from the tested free options
- better source control than aggregator-only intake
- low operational complexity and no obvious quota pressure

Consequence:
- all section builders should expect title + excerpt inputs first
- source ranking and dedupe are mandatory parts of the pipeline

## Decision 2: Aggregator APIs are optional enrichment, not the backbone
**Status:** accepted

NewsAPI and newsdata.io stay behind a feature flag or optional adapter.

Why:
- both were useful for breadth
- neither was strong enough in free-tier text depth or consistency to be the main foundation

Consequence:
- the system must still produce an edition when aggregators are disabled

## Decision 3: Summarization should optimize for structured output over prompt complexity
**Status:** accepted

Keep the current JSON-first schema and a swappable model adapter.

Why:
- structured outputs were reliable in the POC
- the main quality bottleneck was input curation, not schema compliance

Consequence:
- save packet artifacts and model outputs for each run
- improve ranking/filtering before spending time on prompt micro-optimizations

## Decision 4: Market data for MVP stays minimal and indices-only
**Status:** accepted

Use `yfinance` for the daily market snapshot. Keep Alpha Vantage as a fallback only.

Why:
- Yahoo handled the required 4-index set cleanly
- Alpha Vantage was quota-sensitive and less clean on India coverage

Consequence:
- no top-gainers/top-losers requirement in Sprint 1
- market block is a small summary component, not a product pillar

## Decision 5: Delivery path is static HTML + Resend
**Status:** accepted with follow-up

Generate a static HTML edition, host it on a static platform, and send via Resend.

Why:
- local pipeline already proved the shape
- email sending passed the basic API test

Consequence:
- deployment auth/project setup is still required
- sender-domain verification and manual client checks are still required

## Decision 6: Sprint 1 should explicitly preserve adapter boundaries
**Status:** accepted

The implementation should keep clean seams between:
- intake sources
- ranking/filtering
- generation model
- rendering
- delivery

Why:
- almost every dependency from Sprint 0 passed conditionally rather than absolutely
- swapability reduces lock-in and lets us respond to source or pricing changes quickly

## Decision 7: Quality bar beats volume in the first usable version
**Status:** accepted

Prefer fewer strong stories over filling every slot with mediocre ones.

Why:
- the POCs showed how quickly weak intake pollutes downstream summaries
- a smaller, sharper paper is better than a padded one

Consequence:
- empty or shorter sections are acceptable when the candidate pool is weak
- scoring should aggressively punish filler, services/process stories, and rumor-style items

## Open follow-ups
- choose and configure the real static hosting path
- verify Resend sender domain
- run manual Gmail inbox-placement check
- run manual Apple Mail rendering check
- decide whether article-page fetching becomes a Sprint 1 task or a Sprint 2 quality upgrade
