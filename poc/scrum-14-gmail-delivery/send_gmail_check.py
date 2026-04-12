#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = (ROOT / "email_template.html").read_text()
TEXT = """News To Me\n\nYour Morning Paper\nSunday, April 12, 2026\n\nTLDR\n- Inflation jumped after a sharp energy-price spike, keeping pressure on households and policymakers.\n- AI and platform risk stayed in focus after a security incident targeting OpenAI CEO Sam Altman and fresh concerns around Anthropic's new model.\n- Big consumer-tech bets are still moving, with foldable iPhone testing reportedly advancing toward production.\n\nRead the full edition: https://example.com/morning-paper/april-12-2026\n"""
RECIPIENT = "bhargavbangalorevmurthy@gmail.com"
SUBJECT = "Your Morning Paper - April 12, 2026"
SENDER = "News To Me POC <onboarding@resend.dev>"


def build_payload():
    return {
        "from": SENDER,
        "to": [RECIPIENT],
        "subject": SUBJECT,
        "html": HTML,
        "text": TEXT,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="print the payload without sending")
    parser.add_argument("--live", action="store_true", help="send the email through Resend")
    args = parser.parse_args()

    payload = build_payload()
    if args.dry_run or not args.live:
        print(json.dumps({"mode": "dry-run", "request": payload}, indent=2))
        return 0

    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        print("RESEND_API_KEY is required for --live", file=sys.stderr)
        return 1

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

    print(json.dumps({"mode": "live", "request": payload, "response": body}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
