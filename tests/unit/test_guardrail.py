import pytest

from gateway.extraction.guardrail import GuardrailViolationError, verify_verbatim_amount


def test_verbatim_amount_guardrail_success() -> None:
    raw_body = "Tai khoan *4321 vua phat sinh giao dich -75,000 VND tai Highlands Coffee"
    # Should pass without exception
    verify_verbatim_amount(amount=75000, body=raw_body)


def test_verbatim_amount_guardrail_alternate_formats() -> None:
    # Handles decimal dot or pure number
    body_dot = "Giao dich 1.250.000 VND thanh cong"
    verify_verbatim_amount(amount=1250000, body=body_dot)

    body_plain = "GD 50000 VND"
    verify_verbatim_amount(amount=50000, body=body_plain)


def test_verbatim_amount_guardrail_detects_hallucination() -> None:
    raw_body = "Tai khoan *4321 vua phat sinh giao dich -75,000 VND tai Highlands Coffee"
    with pytest.raises(GuardrailViolationError, match="Amount 99000 not found in email body"):
        verify_verbatim_amount(amount=99000, body=raw_body)
