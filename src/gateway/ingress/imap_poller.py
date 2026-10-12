import imaplib
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from gateway.pipeline import GatewayPipeline, PipelineResult

logger = logging.getLogger(__name__)


def normalize_imap_date(date_input: str | None) -> str | None:
    if not date_input:
        return None
    date_str = date_input.strip()
    # Check if already DD-Mon-YYYY (e.g. 01-Jan-2026 or 1-Jan-2026)
    for fmt in ("%d-%b-%Y", "%d-%B-%Y"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%d-%b-%Y")
        except ValueError:
            pass
    # Try ISO YYYY-MM-DD
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d-%b-%Y")
    except ValueError:
        pass
    # Try Year only YYYY
    try:
        dt = datetime.strptime(date_str, "%Y")
        return dt.strftime("01-Jan-%Y")
    except ValueError:
        pass
    return date_str


@dataclass
class IngestionBatchSummary:
    total_found: int
    processed: int
    skipped: int
    errors: int
    results: list[PipelineResult]


class IMAPPoller:
    def __init__(
        self,
        host: str = "imap.gmail.com",
        port: int = 993,
        username: str = "",
        password: str = "",
        pipeline: GatewayPipeline | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.pipeline = pipeline or GatewayPipeline()

    def poll_and_ingest(
        self,
        sender: str = "vib.com.vn",
        since_date: str | None = "01-Jan-2026",
        before_date: str | None = None,
        max_messages: int | None = None,
    ) -> IngestionBatchSummary:
        """
        Polls IMAP mailbox for emails matching the sender criteria and date range (since_date / before_date),
        and streams each raw email payload through the GatewayPipeline.
        """
        clean_pass = self.password.replace(" ", "")
        mail = imaplib.IMAP4_SSL(self.host, self.port)
        try:
            mail.login(self.username, clean_pass)
            mail.select("INBOX", readonly=True)

            query_parts = [f'FROM "{sender}"']
            norm_since = normalize_imap_date(since_date)
            norm_before = normalize_imap_date(before_date)
            if norm_since:
                query_parts.append(f'SINCE "{norm_since}"')
            if norm_before:
                query_parts.append(f'BEFORE "{norm_before}"')
            search_query = f"({' '.join(query_parts)})"
            logger.info(f"IMAP search query: {search_query}")
            typ, data = mail.search(None, search_query)
            msg_ids = data[0].split() if data and data[0] else []

            total_found = len(msg_ids)
            if max_messages and max_messages > 0:
                msg_ids = msg_ids[-max_messages:]

            summary = IngestionBatchSummary(
                total_found=total_found,
                processed=0,
                skipped=0,
                errors=0,
                results=[],
            )

            for mid in msg_ids:
                try:
                    res, msg_data = mail.fetch(mid, "(RFC822)")
                    if not msg_data or not msg_data[0]:
                        continue
                    raw_bytes = msg_data[0][1]
                    result = self.pipeline.process_raw_email(raw_bytes)
                    summary.results.append(result)
                    if result.processed:
                        summary.processed += 1
                    else:
                        summary.skipped += 1
                except Exception as e:
                    summary.errors += 1
                    logger.error(f"Error processing email ID {mid}: {e}")

            return summary
        finally:
            try:
                mail.close()
            except Exception:
                pass
            try:
                mail.logout()
            except Exception:
                pass
