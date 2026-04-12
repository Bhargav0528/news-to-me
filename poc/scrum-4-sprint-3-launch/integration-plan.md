# Sprint 3 integration plan

## Goal
Ship a daily Morning Paper flow that can run unattended, deliver reliably, and feel good enough that Mr. Main actually reads it.

## Recommended work order

### 1. Collapse the POC pieces into one runnable pipeline
Wire these validated parts into one repeatable job:
- RSS-first intake
- optional aggregator enrichment
- market snapshot fetch
- packet scoring and dedupe
- LLM generation through the adapter
- HTML render
- email send
- artifact logging for each run

**Output of this step:** one command that produces a full edition plus stored evidence.

### 2. Make failure states explicit
Add handling for the likely bad paths:
- source fetch timeout or empty section
- market source failure
- model failure or invalid JSON
- HTML render failure
- Resend API failure

**Minimum bar:** a bad dependency should fail visibly and preserve diagnostics, not silently ship garbage.

### 3. Lock the daily operating path
Define the real daily schedule and operator view:
- cron entry and environment source
- output directories and retention
- where logs live
- what counts as a failed run
- whether failed editions are skipped or partially delivered

**Recommendation:** skip delivery if the quality gate fails, but always save diagnostics.

### 4. Verify deliverability and rendering on real clients
The technical send path already passed. Sprint 3 still needs real-world checks:
- verified sender domain in Resend
- one Gmail inbox-placement check
- one Apple Mail rendering check
- one mobile-friendly sanity check

### 5. Run a 5-day unattended launch candidate
Exit criteria in the epic are clear.
For five consecutive days:
- edition generates automatically
- delivery succeeds automatically
- diagnostics are preserved
- no manual babysitting is required
- Mr. Main actually reads the result and flags whether it is worth keeping

## Definition of launch-ready for this epic
Call Sprint 3 ready for launch review only if all of these are true:
- one-command pipeline exists
- failure cases are logged and recoverable
- sender domain is verified
- at least one real mailbox/render test passed
- daily cron is enabled against the integrated path
- five consecutive unattended runs succeeded

## Explicit non-goals
Do not expand scope here unless launch is already stable:
- article-body scraping as a new subsystem
- extra sections just because they seem fun
- mover tables / richer markets widgets
- production-grade web app polish beyond what the static edition needs

## Recommendation
Sprint 3 should stay brutally integration-focused.
The fastest way to miss launch is to reopen product discovery instead of proving the daily loop works.
