# SCRUM-14 Gmail delivery handoff

This folder packages the real-recipient Gmail delivery check without performing the external send from automation.

## Contents
- `email_template.html`, April 12 test email HTML
- `send_gmail_check.py`, reusable send script with dry-run support
- `evidence/draft_payload.json`, exact payload prepared for Resend
- `evidence/dry_run_preview.json`, local dry-run output from the script
- `owner_inbox_check.md`, what the owner should verify in Gmail after sending
- `findings.md`, verdict and caveats

## Run
Dry run:
```bash
python3 send_gmail_check.py --dry-run
```

Manual real send to the intended recipient:
```bash
python3 send_gmail_check.py --live
```
