import email
import email.utils
import re
from datetime import UTC, datetime
from email import policy
from html.parser import HTMLParser

from pydantic import BaseModel


class CleanHTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.result: list[str] = []
        self.skip = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in ("style", "script", "head"):
            self.skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in ("style", "script", "head"):
            self.skip = False

    def handle_data(self, d: str) -> None:
        if not self.skip:
            self.result.append(d)

    def get_text(self) -> str:
        raw = " ".join(self.result)
        return re.sub(r"\s+", " ", raw).strip()


class ParsedEmail(BaseModel):
    message_id: str
    sender: str
    subject: str
    occurred_at: datetime
    body_text: str


def parse_mime_email(raw_bytes: bytes) -> ParsedEmail:
    msg = email.message_from_bytes(raw_bytes, policy=policy.default)

    message_id = msg.get("Message-ID", "")
    if message_id.startswith("<") and message_id.endswith(">"):
        message_id = message_id[1:-1]

    sender = msg.get("From", "")
    subject = msg.get("Subject", "")

    date_header = msg.get("Date")
    if date_header:
        try:
            occurred_at = email.utils.parsedate_to_datetime(date_header)
        except Exception:
            occurred_at = datetime.now(UTC)
    else:
        occurred_at = datetime.now(UTC)

    # Extract body: try text/plain first, then fallback to text/html
    plain_text = ""
    html_text = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" in content_disposition:
                continue

            payload = part.get_payload(decode=True)
            if isinstance(payload, bytes):
                charset = part.get_content_charset() or "utf-8"
                decoded = payload.decode(charset, errors="replace")
                if content_type == "text/plain":
                    plain_text += decoded
                elif content_type == "text/html":
                    html_text += decoded
    else:
        content_type = msg.get_content_type()
        payload = msg.get_payload(decode=True)
        if isinstance(payload, bytes):
            charset = msg.get_content_charset() or "utf-8"
            decoded = payload.decode(charset, errors="replace")
            if content_type == "text/html":
                html_text = decoded
            else:
                plain_text = decoded
        elif isinstance(payload, str):
            if content_type == "text/html":
                html_text = payload
            else:
                plain_text = payload

    if plain_text.strip():
        final_body = plain_text.strip()
    elif html_text.strip():
        extractor = CleanHTMLTextExtractor()
        extractor.feed(html_text)
        final_body = extractor.get_text()
    else:
        final_body = ""

    return ParsedEmail(
        message_id=message_id,
        sender=sender,
        subject=subject,
        occurred_at=occurred_at,
        body_text=final_body,
    )
