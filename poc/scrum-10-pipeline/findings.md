# SCRUM-10, end-to-end pipeline spike

## Verdict
The rough architecture works locally right now.

A single throwaway script can ingest existing POC outputs, generate a usable TLDR-style JSON payload, and render it as a simple HTML page. The main blocker in this run was deployment, not the data flow itself.

## What I wired
- article input from `poc/scrum-8-llm-quality/article_packet.json`
- market input from `poc/scrum-7-stock-data/stock_results.json`
- one script, `run_pipeline.py`, that:
  - loads the POC inputs
  - selects a small story set
  - generates a rough top TLDR object
  - generates a rough Business + Tech section object
  - writes `output/edition.json`
  - renders `output/index.html`

## Deliverables
- `run_pipeline.py`, single-file throwaway pipeline
- `output/edition.json`, generated page payload
- `output/index.html`, simple rendered page
- `vercel.json`, static deploy config
- `deploy_notes.md`, exact deployment blocker + handoff

## Pipeline timing
See `output/edition.json` for exact measured timings from this run.

Practical read: the local pipeline itself is effectively instant. The real future cost is article fetching, prompt calls, and deploy latency, not the page render step.

## What broke or needed manual fixing
- There is no saved Claude response artifact in the repo, only the SCRUM-8 prompt and article packet, so this run generated the rough summary payload directly in the pipeline script.
- Input quality is still uneven because the packet includes some weaker or feature-like stories.
- Vercel deployment could not be completed from this environment because there is no CLI install, token, or linked project config available.

## Live URL status
Not completed in this run.

Reason: deployment was blocked by missing Vercel tooling/auth in the repo environment.

## Confidence at scale
**6/10**

Why not higher:
- the shape works
- the file handoff works
- the rendered output works
- but source quality and article richness are still the real risk
- deployment and true LLM invocation still need to be made repeatable, not manual/implicit

## Recommendation
Treat this as a pass for the architecture and a partial pass for operational readiness.

The next meaningful improvements are:
1. save actual model output artifacts from the LLM-quality step
2. improve source ranking and filtering before summary generation
3. add a real deploy credential path for Vercel or another static host
4. only then judge the full pipeline on repeatability rather than a single local spike
