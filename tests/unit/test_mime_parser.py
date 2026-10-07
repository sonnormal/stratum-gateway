from gateway.ingress.mime_parser import parse_mime_email


def test_mime_parser_extracts_headers_and_body(sample_vib_email_bytes: bytes) -> None:
    email_data = parse_mime_email(sample_vib_email_bytes)

    assert email_data.message_id == "RFC822-MSG-20261006-VIB-001@vib.com.vn"
    assert "alert@vib.com.vn" in email_data.sender
    assert "Thong bao bien dong so du" in email_data.subject
    assert "Highlands Coffee" in email_data.body_text
    assert email_data.occurred_at is not None
