# SCRUM-14, real Gmail delivery check

## Verdict
Prepared for review, but the actual real-recipient send and Gmail placement verification were intentionally left as a manual owner step.

## Why the send was not executed here
This ticket explicitly targets a real external recipient, `bhargavbangalorevmurthy@gmail.com`.
Per the workspace guardrail for external actions, this automation pass did not send that message directly.
Instead, it packaged the exact April 12 payload, reusable send script, and owner verification checklist so the final live step can happen deliberately.

## What I completed
- reused the SCRUM-9 Resend approach and template structure
- updated the email content for the requested April 12, 2026 subject line
- used sample TLDR content derived from SCRUM-8 and SCRUM-10 artifacts
- included the required fake newspaper URL in the body
- prepared a dedicated send script for the real Gmail recipient with `--dry-run` and `--live` modes
- captured the exact payload that should be sent through Resend
- documented the Gmail checks still needed from the owner

## Deliverables
- `email_template.html`
- `send_gmail_check.py`
- `evidence/draft_payload.json`
- `evidence/dry_run_preview.json`
- `owner_inbox_check.md`
- `README.md`

## Remaining manual step
This email should go to: `bhargavbangalorevmurthy@gmail.com`

To finish the real delivery check, run:
```bash
cd /home/bbv/.openclaw/workspace/peeohsee-1/projects/news-to-me/poc/scrum-14-gmail-delivery
source ../../.env
python3 send_gmail_check.py --live
```

Then capture:
- API response
- Gmail placement: Primary / Promotions / Spam
- screenshot of Gmail rendering
- any rendering or warning-banner issues

## Review call
This ticket is ready for review as a prepared handoff bundle, but it is not yet evidence of successful Gmail delivery until the owner performs the live send and records the inbox result.
