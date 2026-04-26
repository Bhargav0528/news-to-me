"""Email publishing via AgentMail API — replaces Gmail SMTP."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

try:
    from agentmail import AgentMail
except ImportError:
    AgentMail = None


@dataclass
class EmailConfig:
    """Runtime configuration for AgentMail email delivery."""

    api_key: str = os.getenv('AGENTMAIL_API_KEY', '')
    inbox_id: str = os.getenv('AGENTMAIL_INBOX_ID', 'mrmain@agentmail.to')
    recipient: str = os.getenv('EMAIL_TO', 'bhargavbangalorevmurthy@gmail.com')
    edition_url: str = os.getenv('EDITION_URL', 'https://web-sand-two-88.vercel.app')


class EmailPublisher:
    """Render and send an edition email via AgentMail API."""

    def __init__(self, config: EmailConfig | None = None) -> None:
        load_dotenv()
        # Resolve env vars at instance creation, not class definition
        self.config = config or EmailConfig(
            api_key=os.getenv('AGENTMAIL_API_KEY', ''),
            inbox_id=os.getenv('AGENTMAIL_INBOX_ID', 'mrmain@agentmail.to'),
            recipient=os.getenv('EMAIL_TO', 'bhargavbangalorevmurthy@gmail.com'),
            edition_url=os.getenv('EDITION_URL', 'https://web-sand-two-88.vercel.app'),
        )

    def build_subject(self, edition: dict[str, Any]) -> str:
        """Build the email subject for an edition."""
        return f"News To Me, {edition['date']}"

    def build_text(self, edition: dict[str, Any]) -> str:
        """Render a plain-text email body from the edition."""
        url = edition.get('_live_url', self.config.edition_url)
        date = edition.get('date', 'unknown')
        generated_at = edition.get('generated_at', '')
        version = edition.get('_version_hash', 'unknown')
        lines = [
            'News To Me',
            '',
            f"Edition date: {date}",
            f"Generated: {generated_at}",
            f"Version: {version}",
            f"Read online: {url}",
            '',
            'TLDR',
        ]
        for item in edition['tldr']:
            lines.append(f"- {item['headline']}: {item['summary']}")
        lines.extend([
            '',
            'Sections included:',
            f"- News regions: {', '.join(edition['news'].keys())}",
            f"- Biz/Tech articles: {len(edition['biztech']['articles'])}",
            f"- Growth: {edition.get('growth', {}).get('title', 'unavailable')}",
            f"- Knowledge: {edition.get('knowledge', {}).get('title', 'unavailable')}",
            f"- Riddle: {edition.get('fun', {}).get('riddle', {}).get('question', 'unavailable')}",
        ])
        return '\n'.join(lines)

    def build_html(self, edition: dict[str, Any]) -> str:
        """Render a styled HTML email body from the edition."""
        tldr_items = ''.join(
            f"<li><strong>{item['headline']}</strong><br>{item['summary']}</li>"
            for item in edition.get('tldr', [])
        )
        url = edition.get('_live_url', self.config.edition_url)
        date = edition.get('date', 'unknown')
        generated_at = edition.get('generated_at', '')
        version = edition.get('_version_hash', 'unknown')
        return f"""<!doctype html>
<html lang='en'>
  <body style='margin:0;background:#f8fafc;color:#0f172a;font-family:Arial,sans-serif;'>
    <div style='max-width:720px;margin:24px auto;padding:24px;background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;'>
      <p style='margin:0 0 8px;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#64748b;'>News To Me</p>
      <h1 style='margin:0 0 8px;font-size:28px;line-height:1.2;'>Your Morning Paper</h1>
      <p style='margin:0 0 4px;color:#475569;font-size:14px;'>
        Edition: <strong>{date}</strong>
        &nbsp;|&nbsp; Generated: <strong>{generated_at}</strong>
        &nbsp;|&nbsp; Version: <code>{version}</code>
      </p>
      <a href='{url}' style='display:inline-block;margin:0 0 20px;padding:8px 16px;background:#2563eb;color:#ffffff;text-decoration:none;border-radius:6px;font-size:14px;'>Read Full Edition →</a>
      <h2 style='margin:0 0 10px;font-size:18px;'>TLDR</h2>
      <ul style='margin:0 0 20px;padding-left:20px;color:#334155;line-height:1.6;'>
        {tldr_items}
      </ul>
      <p style='margin:0 0 16px;color:#334155;line-height:1.6;'><strong>Growth:</strong> {edition.get('growth', {}).get('title', 'unavailable')}</p>
      <p style='margin:0 0 16px;color:#334155;line-height:1.6;'><strong>Knowledge:</strong> {edition.get('knowledge', {}).get('title', 'unavailable')}</p>
      <a href='{url}' style='display:inline-block;margin:0 0 16px;padding:8px 16px;background:#2563eb;color:#ffffff;text-decoration:none;border-radius:6px;font-size:14px;'>Read Full Edition →</a>
      <p style='margin:0;color:#64748b;font-size:12px;line-height:1.5;'>Version <code>{version}</code> &nbsp;|&nbsp; Generated {generated_at} &nbsp;|&nbsp; <a href='{url}'>{url}</a></p>
    </div>
  </body>
</html>"""

    def send(self, edition: dict[str, Any]) -> None:
        """Send the edition via AgentMail API."""
        if AgentMail is None:
            raise RuntimeError(
                "agentmail package not installed. Run: pip install agentmail"
            )

        api_key = self.config.api_key
        if not api_key:
            raise RuntimeError(
                "AGENTMAIL_API_KEY env var is required. "
                "Get your key from console.agentmail.to"
            )

        client = AgentMail(api_key=api_key)
        subject = self.build_subject(edition)
        text = self.build_text(edition)
        html = self.build_html(edition)

        client.inboxes.messages.send(
            inbox_id=self.config.inbox_id,
            to=self.config.recipient,
            subject=subject,
            text=text,
            html=html,
        )

    def write_preview(self, edition: dict[str, Any], output_path: str | Path) -> Path:
        """Write a local JSON preview of the outbound email payload."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            'subject': self.build_subject(edition),
            'to': self.config.recipient,
            'inbox_id': self.config.inbox_id,
            'text': self.build_text(edition),
            'html': self.build_html(edition),
        }
        output.write_text(json.dumps(payload, indent=2))
        return output