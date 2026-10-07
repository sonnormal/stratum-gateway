from typing import Any

from gateway.egress.viber_client import format_viber_alert_message


def test_viber_message_formatter(mock_ollama_extraction: dict[str, Any]) -> None:
    message = format_viber_alert_message(mock_ollama_extraction)

    assert "[VIB]" in message
    assert "75,000" in message or "75000" in message
    assert "Highlands Coffee" in message
    assert "Food & Beverage" in message
