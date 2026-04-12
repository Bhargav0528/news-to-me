# SCRUM-7, stock data source POC

## Verdict
Use Yahoo Finance via `yfinance` as the primary free source for daily index data.
Use Alpha Vantage as a secondary fallback only, and treat its movers feed as US-only and noisy.

## Why
- `yfinance` cleanly returned all 4 required market indices in 3/3 runs: S&P 500, NASDAQ, NIFTY 50, SENSEX.
- Alpha Vantage can cover the US pair directly and can approximate the India pair via India ETFs (`NIFTYBEES.BSE`, `SENSEXBEES.BSE`), but not the exact headline indices as cleanly.
- Alpha Vantage free tier is touchy in practice. Fast back-to-back calls returned rate-limit payloads instead of quotes, so it is not a great primary backbone for a simple multi-symbol fetch unless we deliberately serialize and throttle requests.

## What I tested
### Yahoo Finance / `yfinance`
- `^GSPC` for S&P 500
- `^IXIC` for NASDAQ Composite
- `^NSEI` for NIFTY 50
- `^BSESN` for SENSEX
- repeated the full 4-index pull 3 times

### Alpha Vantage
Initial burst test:
- `GLOBAL_QUOTE` for `SPY`, `QQQ`, `NIFTYBEES.BSE`, `SETS.BSE`
- `TOP_GAINERS_LOSERS`
- repeated over 3 runs

Follow-up paced/manual checks, after slowing down requests to avoid false negatives from free-tier burst limiting:
- `GLOBAL_QUOTE` for `QQQ`
- `GLOBAL_QUOTE` for `NIFTYBEES.BSE`
- `GLOBAL_QUOTE` for `SENSEXBEES.BSE`
- `TOP_GAINERS_LOSERS`
- `SYMBOL_SEARCH` for `NIFTY 50`
- `SYMBOL_SEARCH` for `SENSEX`

## Sample output for each required index
### Yahoo Finance, exact indices
- **S&P 500** (`^GSPC`)
  - value: `6816.8901`
  - change: `-7.7700`
  - change_percent: `-0.1139%`
- **NASDAQ Composite** (`^IXIC`)
  - value: `22902.8906`
  - change: `80.4707`
  - change_percent: `0.3526%`
- **NIFTY 50** (`^NSEI`)
  - value: `24050.5996`
  - change: `275.5000`
  - change_percent: `1.1588%`
- **SENSEX** (`^BSESN`)
  - value: `77550.2500`
  - change: `918.6016`
  - change_percent: `1.1987%`

### Alpha Vantage, usable direct/fallback symbols
Important caveat: this is not the same thing as exact index support for the India pair. The successful India symbols were ETFs, not the raw NIFTY 50 / SENSEX index tickers.

- **US proxy for S&P 500** (`SPY`)
  - value: `679.46`
  - change: `-0.45`
  - change_percent: `-0.0662%`
- **US proxy for NASDAQ** (`QQQ`)
  - value: `611.07`
  - change: `0.88`
  - change_percent: `0.1442%`
- **India proxy for NIFTY 50** (`NIFTYBEES.BSE` ETF)
  - value: `272.01`
  - change: `2.53`
  - change_percent: `0.9388%`
- **India proxy for SENSEX** (`SENSEXBEES.BSE` ETF)
  - value: `884.59`
  - change: `8.32`
  - change_percent: `0.9495%`

## Reliability assessment
### Yahoo Finance / `yfinance`
Strong in this POC.

Observed result:
- all 4 required indices succeeded in **3/3 runs**
- values and daily change percentages were identical across the repeat runs in this end-of-day snapshot
- US and India coverage both worked cleanly

Practical read:
- for daily market snapshot use, this looks good enough for the MVP
- biggest risk is the one already noted in the Jira ticket: `yfinance` is unofficial and could break if Yahoo changes underlying endpoints

### Alpha Vantage
Mixed.

Observed result:
- initial burst run produced repeated free-tier limit messages after the first successful quote, so naive back-to-back querying is fragile
- after pacing requests, `QQQ`, `NIFTYBEES.BSE`, `SENSEXBEES.BSE`, and `TOP_GAINERS_LOSERS` all responded
- exact India headline-index discovery was weak, with `SYMBOL_SEARCH` for `NIFTY 50` returning no match in this run

Practical read:
- Alpha Vantage can work, but only if we serialize requests and accept imperfect symbol mapping, especially for India
- it is a weaker fit as the main source for a tiny daily market section because it adds throttle complexity without giving better coverage than Yahoo

## Can we get top 5 gainers/losers from each market?
### Yahoo Finance / `yfinance`
Not validated as a clean built-in path in this POC.

Practical answer:
- for the specific library path tested here, I did **not** validate a simple reliable marketwide top-gainers/top-losers endpoint for either US or India
- if we need movers from Yahoo later, that likely becomes a separate scrape/endpoint-specific experiment, not a quick freebie from the same exact index flow

### Alpha Vantage
Partially yes, but only for the US market.

Observed result:
- `TOP_GAINERS_LOSERS` returned a populated list of US tickers
- sample top 5 from the response:
  1. `FUSE` `+115.2941%`
  2. `RAYA` `+107.4422%`
  3. `MAPSW` `+100.0%`
  4. `CREG` `+85.4081%`
  5. `SLXNW` `+82.1429%`

Important caveat:
- this feed is clearly **US-only** from the API metadata
- the returned movers are noisy and include very small-cap / warrant-style tickers, which is probably wrong for a polished newspaper product unless we add filtering rules
- I did **not** find evidence in this POC of a clean equivalent India top-gainers/top-losers feed on Alpha Vantage free tier

## Quota fit
### Alpha Vantage free tier
The ticket note said 25 requests/day. This POC aligns with that.

If we used Alpha Vantage for a once-daily market block:
- 4 symbol lookups + 1 movers call = **5 requests/day**
- that is technically within quota

But the real issue is not only daily quota. It is pacing and fragility:
- free-tier requests must be slowed down carefully
- if we ever add retries, more symbols, or multiple editions/day, the quota margin gets thin fast

## Recommendation
### Primary
Use **Yahoo Finance via `yfinance`** for the daily index snapshot.

Why:
- exact support for all 4 required indices in this POC
- cleaner US + India coverage than Alpha Vantage for the specific requirement
- consistent 3-run result in this end-of-day test

### Fallback / optional enrichment
Use **Alpha Vantage** only as:
- a backup quote source, or
- a US-only movers feed if we decide we want one and are willing to filter junk tickers aggressively

### Product implication
For the MVP, I would keep the market box simple:
- S&P 500
- NASDAQ
- NIFTY 50
- SENSEX
- value + daily change + change percent

I would **not** make top movers a required MVP element yet.
The US movers feed is noisy, and India movers were not validated cleanly in this POC.

## Bottom line
- **Yahoo Finance passed** for the exact index requirement
- **Alpha Vantage partially passed** for fallback quotes and US movers, but not as the clean primary source
- **Primary vs fallback recommendation:** Yahoo first, Alpha Vantage second

## Deliverables in this folder
- `run_stock_checks.py`, reproducible validation script
- `stock_results.json`, repeat-run output from the initial automated run
- `alpha_vantage_manual_checks.json`, slowed follow-up checks that separate symbol support from burst limiting
- `samples/run-*.json`, per-run raw snapshots
