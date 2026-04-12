# Sprint 3 risk register

## 1. Editorial quality still misses the bar
- **Why it matters:** a stable bad paper is still a bad launch
- **Early warning:** thin institutional/process filler keeps leaking into Top Stories or Biz + Tech
- **Mitigation:** keep source curation and scoring ahead of cosmetic polish; prefer fewer stronger items

## 2. Free-source text depth is too weak
- **Why it matters:** titles + snippets can produce flat summaries
- **Early warning:** sections feel repetitive, vague, or under-explained even when the model behaves
- **Mitigation:** tighten packet curation now; defer article-page fetch/cleaning as the next major quality upgrade if needed

## 3. Delivery passes technically but lands badly
- **Why it matters:** API success is not the same as inbox placement or readable rendering
- **Early warning:** mail goes to spam, clips badly, or looks broken in Apple Mail/mobile
- **Mitigation:** verify sender domain, run real mailbox checks, keep HTML conservative

## 4. Cron appears healthy but the daily loop is brittle
- **Why it matters:** launch criteria require unattended success, not one lucky run
- **Early warning:** transient fetch/model/send failures need manual reruns or log spelunking
- **Mitigation:** make every stage fail loudly, persist diagnostics, and test the full chain for 5 straight days

## 5. Market dependency breaks
- **Why it matters:** the markets box is small but highly visible
- **Early warning:** `yfinance` starts failing or returns stale/partial index data
- **Mitigation:** keep the box minimal and preserve Alpha Vantage or another fallback path

## 6. Scope creep reopens discovery
- **Why it matters:** Sprint 3 is where projects die by trying to become smarter instead of more reliable
- **Early warning:** new sections, richer scraping, or product redesigns start displacing integration work
- **Mitigation:** treat launch stability as the only priority until the 5-day proof is complete

## Recommendation
The biggest launch risk is not one broken API.
It is losing focus and shipping an unstable or mediocre daily experience because Sprint 3 tried to do invention instead of integration.
