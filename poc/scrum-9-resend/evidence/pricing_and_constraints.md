# Resend pricing and setup notes

Source checked: `https://resend.com/pricing` and Resend docs pages on sending + domains.

Key points captured for this POC:
- Free tier: 3,000 emails/month
- Free tier daily cap: 100 emails/day
- Free tier includes 1 domain
- Production sending should use a verified domain you own
- Resend docs recommend a subdomain for sender reputation isolation
- For testing, Resend documents `onboarding@resend.dev` as the test sender
- The configured API key in this workspace is restricted to sending only, so account/domain inspection endpoints return authorization errors

Domain verification steps needed for production:
1. Add a subdomain in Resend, for example `updates.example.com`
2. Publish SPF and DKIM DNS records provided by Resend
3. Optionally add DMARC for stronger mailbox trust
4. Switch the `from` address from `onboarding@resend.dev` to the verified subdomain sender
