from unittest.mock import MagicMock, patch

from gateway.ingress.imap_poller import IMAPPoller
from gateway.pipeline import PipelineResult


def test_imap_poller_mock_poll_and_ingest():
    mock_pipeline = MagicMock()
    mock_pipeline.process_raw_email.return_value = PipelineResult(
        processed=True,
        event_id="test-event-id",
        movement_status="RECORDED",
    )

    with patch("imaplib.IMAP4_SSL") as mock_imap_cls:
        mock_imap = MagicMock()
        mock_imap_cls.return_value = mock_imap
        mock_imap.login.return_value = ("OK", [b"Logged in"])
        mock_imap.select.return_value = ("OK", [b"10"])
        mock_imap.search.return_value = ("OK", [b"101 102"])
        mock_imap.fetch.return_value = ("OK", [(b"101 (RFC822 {10})", b"From: info@myvib.vib.com.vn\n\nTest")])

        poller = IMAPPoller(
            username="test@example.com",
            password="testpassword",
            pipeline=mock_pipeline,
        )

        summary = poller.poll_and_ingest(
            sender="vib.com.vn",
            since_date="2026-01-01",
            before_date="2026-12-31",
            max_messages=1,
        )

        assert summary.total_found == 2
        assert summary.processed == 1
        assert summary.skipped == 0
        assert summary.errors == 0
        assert len(summary.results) == 1
        assert summary.results[0].movement_status == "RECORDED"
        mock_pipeline.process_raw_email.assert_called_once()
        mock_imap.search.assert_called_once_with(
            None, '(FROM "vib.com.vn" SINCE "01-Jan-2026" BEFORE "31-Dec-2026")'
        )


def test_normalize_imap_date():
    from gateway.ingress.imap_poller import normalize_imap_date

    assert normalize_imap_date("01-Jan-2026") == "01-Jan-2026"
    assert normalize_imap_date("2026-05-15") == "15-May-2026"
    assert normalize_imap_date("2026") == "01-Jan-2026"
    assert normalize_imap_date(None) is None

