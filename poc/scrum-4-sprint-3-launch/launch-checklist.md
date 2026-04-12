# Sprint 3 launch checklist

## Integration
- [ ] Replace isolated POC scripts with one integrated runner
- [ ] Persist intermediate artifacts for each run
- [ ] Confirm section scoring/dedupe are applied before generation
- [ ] Confirm market snapshot is included in the final edition
- [ ] Confirm HTML output is the same artifact used for delivery

## Reliability
- [ ] Empty or thin source packets fail visibly
- [ ] Invalid model output fails visibly
- [ ] Delivery API errors fail visibly
- [ ] Cron exits non-zero on real failure
- [ ] Logs and diagnostics are easy to inspect after a run

## Delivery readiness
- [ ] Resend sender domain verified
- [ ] Gmail inbox placement checked manually
- [ ] Apple Mail rendering checked manually
- [ ] Mobile sanity check completed

## Editorial quality gate
- [ ] Edition has enough strong stories to feel worth opening
- [ ] Weak filler does not dominate Top Stories
- [ ] Business + Tech is not mostly aggregator sludge
- [ ] Explainer / Learn / Fun are not repetitive or limp
- [ ] Markets box is simple, accurate, and stable

## Launch proof
- [ ] Daily cron points at the integrated runner
- [ ] Environment/config path is documented
- [ ] 5 consecutive unattended days succeeded
- [ ] Mr. Main read the launch-candidate editions
- [ ] Mr. Main agrees the product is good enough to keep shipping

## Recommended final go/no-go rule
If the system is technically stable but the edition is still not worth reading, do **not** call it launched.
This epic only counts as a success when reliability and reader value both clear the bar.
