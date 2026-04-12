# Manual inbox check still required

The machine-verifiable part of this POC is done.

To fully close the original Jira ask, a human still needs to:

1. Run the send script against a Gmail address they control:
   - `RESEND_TO="your-gmail@example.com" python3 send_resend_check.py`
2. Open Gmail and record whether the email landed in:
   - Primary
   - Promotions
   - Spam
3. Open the same message in Apple Mail or another second client and confirm:
   - layout is intact
   - CTA link is visible
   - bullet list spacing looks normal
4. Save screenshots of the received message in Gmail and the second client.

Recommended recipient targets for the manual step:
- Gmail inbox controlled by Mr. Main
- Apple Mail account controlled by Mr. Main

Notes:
- The configured API key is send-only, so this POC can send but cannot inspect domain state or message analytics via the broader account endpoints.
- Production use should switch `from` away from `onboarding@resend.dev` to a verified subdomain, after DNS verification is completed in Resend.
