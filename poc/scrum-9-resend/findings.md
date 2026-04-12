# SCRUM-9, Resend email delivery POC

## Verdict
Resend passed for the basic MVP send path.
The API can send a styled HTML email successfully on the free tier, but inbox placement in Gmail and rendering in Apple Mail are still unverified from this environment.

## What I tested
- confirmed current documented free-tier limits from Resend pricing and docs
- confirmed that the configured API key is send-only
- sent a styled HTML test email through Resend using the documented test sender `onboarding@resend.dev`
- targeted Resend's documented test recipient `delivered@resend.dev`
- saved a reusable HTML template and a runnable Python send script for manual mailbox checks

## Evidence
### API send result
- successful POST to `https://api.resend.com/emails`
- response id: `4043e351-31c0-4f4d-9113-8bf499f23147`
- request/response snapshot saved in `evidence/send_response.json`

### Free-tier fit
- free tier still advertises `3,000 emails/month`
- free tier still advertises `100 emails/day`
- for one morning-paper edition per day, that is comfortably inside quota for an MVP or solo pilot

### Sender/domain constraints
- the current API key can send email, but it is restricted and cannot inspect broader account/domain endpoints
- production delivery should not keep using `onboarding@resend.dev`
- production delivery should move to a verified subdomain after SPF and DKIM are added in DNS

## What this POC does not prove yet
The original ticket asked for inbox placement and cross-client rendering evidence.
I could not complete those two checks from this environment because they require access to a real recipient mailbox/client.

Still unverified:
- did the message land in Gmail Primary vs Promotions vs Spam
- did the exact same HTML render cleanly in Apple Mail
- screenshot evidence from a real mailbox

## Recommendation
Use Resend as the MVP email sender.

Why:
- the free-tier quota is enough for the current scope
- the send API is simple and worked immediately with a styled HTML payload
- the test-domain path is good enough for development while the real sender domain is being prepared

But before launch:
- verify a real sender subdomain in Resend
- run one manual Gmail send and record inbox placement
- open the same message in Apple Mail and save screenshots

## Deliverables in this folder
- `email_template.html`, the styled HTML template used for the test
- `send_resend_check.py`, runnable send script
- `evidence/send_response.json`, API evidence from the successful send
- `evidence/pricing_and_constraints.md`, captured free-tier + domain notes
- `manual_inbox_check.md`, exact follow-up steps for Gmail and Apple Mail validation

## Bottom line
- API send path, passed
- free-tier quota, passed
- production sender-domain setup, still required
- Gmail inbox placement and Apple Mail rendering, manual follow-up still required before claiming full delivery confidence
