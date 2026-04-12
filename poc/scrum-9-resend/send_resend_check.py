#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = (ROOT / "email_template.html").read_text()
TEXT = """News To Me\n\nYour Morning Paper\nSunday, April 11, 2026\n\nTLDR\n- Global markets finished mixed as investors balanced strong US tech momentum against inflation and policy uncertainty.\n- India business coverage stayed active around regulation, capital flows, and earnings positioning.\n- AI and semiconductor coverage remained the strongest cross-market tech theme.\n\nRead the full edition: https://example.com/morning-paper\n"""

def main() -> int:
    api_key = os.environ.get("RESEND_API_KEY")
    recipient = os.environ.get("RESEND_TO", "delivered@resend.dev")
    sender = os.environ.get("RESEND_FROM", "News To Me POC <onboarding@resend.dev>")
    if not api_key:
        print("RESEND_API_KEY is required", file=sys.stderr)
        return 1

    payload = {
        "from": sender,
        "to": [recipient],
        "subject": "Your Morning Paper - April 11, 2026",
        "html": HTML,
        "text": TEXT,
    }

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "curl/8.5.0",
        },
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode())

    print(json.dumps({"request": payload, "response": body}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
