# Sprint 1 architecture decisions after completed Sprint 0 review v2

## Decision 1: Intake stays RSS-first, but local coverage now has a defined primary source set
**Status:** accepted

Use curated publisher feeds as the intake backbone.

Primary set now includes:
- Deccan Herald for Bangalore/Karnataka local
- New Indian Express Bengaluru + Karnataka as supplementary local/state coverage
- The Hindu for India
- Guardian US for US general
- BBC World for world
- BusinessLine + CNBC for business
- TechCrunch with Ars Technica as secondary tech enrichment

## Decision 2: Article-page fetching is now a Sprint 1 requirement, not a later optional upgrade
**Status:** accepted

Why:
- SCRUM-18 showed a large quality gain from full text over excerpts
- excerpt fallback is still necessary for blocked or weak publishers

Consequence:
- pipeline should persist fetch status, fetch method, and full text length
- section generation should prefer full text when present

## Decision 3: AgentMail replaces Resend for this validated delivery path
**Status:** accepted

Why:
- live-recipient delivery succeeded through AgentMail
- the tested Resend path was blocked/unreliable for this use case

Consequence:
- email delivery adapter should target AgentMail first for Sprint 1 in this project context
- keep rendering and inbox-placement checks in the QA loop

## Decision 4: Growth and Knowledge can ship with tightened prompts; Fun/Puzzles needs a quality gate
**Status:** accepted with caution

Why:
- Growth and Knowledge outputs were good enough to proceed with prompt refinements
- Fun/Puzzles still lacks strong enough guarantees for uniqueness and puzzle depth

Consequence:
- prompt files should be made explicit and versioned in repo
- Fun/Puzzles should either ship in a constrained mode or stay behind an internal quality gate

## Decision 5: Quality-first edition shaping remains the right MVP rule
**Status:** accepted

Prefer fewer strong stories over filling all slots with weak material.

Why:
- source and fetch quality vary by publisher
- full-text support helps, but not every story benefits equally

## Open follow-ups
- confirm Gmail inbox placement and rendering for the corrected AgentMail send
- make Growth / Knowledge / Fun prompt files explicit in the project tree
- add stronger automated validation if Fun/Puzzles must guarantee uniqueness and correctness
- finalize the static deployment path
