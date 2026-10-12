from typing import Any
from unittest.mock import MagicMock, patch

from gateway.egress.telegram_client import TelegramClient, format_telegram_alert_message


def test_telegram_message_formatter(mock_ollama_extraction: dict[str, Any]) -> None:
    message = format_telegram_alert_message(mock_ollama_extraction)
    assert "[VIB] Biến động: -75,000 VND" in message
    assert "Highlands Coffee" in message
    assert "Food & Beverage" in message


def test_telegram_client_send_alert_success():
    client = TelegramClient(bot_token="test_token", default_chat_id="123456789")

    with patch("httpx.Client.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True, "result": {"message_id": 1}}
        mock_post.return_value = mock_response

        success = client.send_alert("Test message")
        assert success is True
        mock_post.assert_called_once_with(
            "https://api.telegram.org/bottest_token/sendMessage",
            json={"chat_id": "123456789", "text": "Test message"},
        )


def test_telegram_client_dry_run_without_token():
    client = TelegramClient(bot_token="", default_chat_id="")
    # Should cleanly return True in mock/dry-run mode
    assert client.send_alert("Test message") is True
