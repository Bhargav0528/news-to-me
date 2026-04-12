# SCRUM-10 deployment notes

## What works now
- `run_pipeline.py` reads the existing POC inputs and generates:
  - `output/edition.json`
  - `output/index.html`
- The output is already shaped so Vercel can serve it as a static site.
- `vercel.json` points Vercel at the `output/` directory.

## What blocked deployment in this run
- `vercel` CLI is not installed in the current environment.
- No Vercel auth token or linked project config is present in this repo.
- Per workspace rules, external publication should not be improvised without the needed credentials/config.

## Next step to get a live URL
From this folder, after Vercel access is configured:

```bash
python3 run_pipeline.py
npx vercel --prod
```

If preferred, the same folder can also be connected through GitHub import and published as a static site with `output/` as the output directory.
