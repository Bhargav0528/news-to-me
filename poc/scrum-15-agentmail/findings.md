# SCRUM-15, AgentMail replacement POC

## Goal
Validate AgentMail as a replacement for the blocked Resend onboarding send path and send a real test email to bhargavbangalorevmurthy@gmail.com.

## Evidence
- AgentMail skill installed via ClawHub into `/home/bbv/.openclaw/workspace/skills/agentmail`
- OpenClaw config updated with `AGENTMAIL_API_KEY`
- Existing inbox discovered: `mrmain@agentmail.to`
- Live send attempted from AgentMail using the existing inbox

## Live send result
The live AgentMail send succeeded.

- Sender inbox: `mrmain@agentmail.to`
- Recipient: `bhargavbangalorevmurthy@gmail.com`
- Message ID: `<0100019d83a40211-d4ad7659-a7c4-4f8f-b13c-ead6b7cb521d-000000@email.amazonses.com>`
- Thread ID: `46992cd3-c4dc-4690-9daf-d53724123061`

## Recommendation
Yes, AgentMail is a viable replacement for the blocked Resend onboarding path for this use case.

Why:
- skill installation worked
- API key configuration worked
- existing inbox discovery worked
- real external recipient sends succeeded
- the formatting bug was corrected and a second send went out with the actual HTML body content

## Send notes
- first AgentMail send succeeded but used the HTML file path string because of a caller bug
- corrected AgentMail send also succeeded and used the actual HTML body contents
- corrected message id: `<0100019d83a9897b-5abb70c4-3c76-4b9a-9242-f5643c8c74a2-000000@email.amazonses.com>`
- corrected thread id: `68d7d3eb-8805-4112-8fa7-33e6ba78016f`

## Still needed from owner
Please check `bhargavbangalorevmurthy@gmail.com` and confirm:
- did the corrected email land in Primary, Promotions, or Spam
- screenshot of Gmail rendering
- any warning banners or rendering issues
