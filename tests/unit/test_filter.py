from gateway.ingress.filter import is_bank_transaction_email
from gateway.ingress.mime_parser import parse_mime_email


def test_heuristic_filter_detects_bank_emails(
    sample_vib_email_bytes: bytes, sample_non_bank_email_bytes: bytes
) -> None:
    vib_email = parse_mime_email(sample_vib_email_bytes)
    non_bank_email = parse_mime_email(sample_non_bank_email_bytes)

    assert is_bank_transaction_email(vib_email) is True
    assert is_bank_transaction_email(non_bank_email) is False


def test_heuristic_filter_detects_vietnamese_accented_keywords():
    from datetime import UTC, datetime
    from gateway.ingress.mime_parser import ParsedEmail

    email = ParsedEmail(
        message_id="test-123",
        sender="info@myvib.vib.com.vn",
        subject="Chuyển tiền nhanh đến tài khoản ngân hàng nội địa thành công",
        occurred_at=datetime.now(UTC),
        body_text="Quý khách vừa chuyển tiền thành công.",
    )
    assert is_bank_transaction_email(email) is True

