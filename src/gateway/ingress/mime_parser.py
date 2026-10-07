import email
import email.utils
from datetime import UTC, datetime
from email import policy

from pydantic import BaseModel


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

    # Extract body
    body_text = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    charset = part.get_content_charset() or "utf-8"
                    body_text += payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if isinstance(payload, bytes):
            charset = msg.get_content_charset() or "utf-8"
            body_text = payload.decode(charset, errors="replace")
        elif isinstance(payload, str):
            body_text = payload

    return ParsedEmail(
        message_id=message_id,
        sender=sender,
        subject=subject,
        occurred_at=occurred_at,
        body_text=body_text.strip(),
    )
