# SCRUM-3, Sprint 2 generate + publish spike

## Verdict
Proceed.

A full 7-section edition can now be assembled from real saved News To Me artifacts and rendered as a readable static HTML page. The pipeline shape is viable enough to move SCRUM-3 into review, but deployment and stronger editorial ranking are still open follow-through items.

## What this package does
This spike proves the missing middle layer between the Sprint 1 foundation work and the final launch sprint:
- reads real article rows from the Sprint 1 SQLite intake artifact
- selects stories for India, World, US, Business, and Technology sections
- adds a TLDR layer that reflects the section packet
- adds the validated 4-index market snapshot from SCRUM-7
- renders the result into a static HTML page with all 7 sections populated

## Deliverables
- `README.md`
- `findings.md`
- `run_generate_publish_spike.py`
- `sample_output/edition.json`
- `sample_output/diagnostics.json`
- `sample_output/index.html`

## Verification result
Local run passed.

Observed outputs:
- all 7 sections were populated
- editorial sections pulled from the saved Sprint 1 foundation database, not made-up placeholders
- market section pulled from the validated Yahoo Finance snapshot path
- the generated HTML page is readable and can be opened locally as a static artifact

## What this validates
### 1. Section assembly is now concrete
SCRUM-2 proved collection and storage. This spike proves those saved intake artifacts are already sufficient to build a newspaper-shaped edition object.

### 2. Static publish format is still the right MVP shape
A single generated `index.html` is enough for local review and is compatible with the earlier static-hosting plan.

### 3. The next bottleneck is quality, not basic feasibility
The pipeline can produce a complete edition shape now. The real remaining work is better ranking, filtering, story selection, and final deployment plumbing.

## Caveats
- story ranking is deterministic and heuristic, not final editorial logic
- TLDR copy is template-driven, not model-written in this spike
- no live deployment URL was produced in this environment
- there is still no proof yet that all 7 sections will be high quality every day under live input drift

## Recommendation
Keep SCRUM-3 moving, but treat the next implementation priorities as:
1. promote this spike into the real project structure
2. tighten ranking and anti-filler rules before broadening volume
3. wire the real model adapter into section writing where it materially helps
4. finish the static-host deployment path

## Bottom line
SCRUM-3 is no longer blocked on architecture ambiguity.

The generate-and-publish layer now has runnable evidence, a complete local artifact, and a clear path to the next refinement step.
