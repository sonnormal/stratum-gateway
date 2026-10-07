import pytest

from gateway.extraction.ollama_client import OllamaExtractionClient


@pytest.mark.integration
def test_ollama_client_live_extraction() -> None:
    client = OllamaExtractionClient(
        host_url="http://localhost:11434",
        model="qwen3.6:27b",
        timeout=60.0,
    )
    email_text = """
    Tai khoan *4321 vua phat sinh giao dich -75,000 VND tai Highlands Coffee.
    Loai GD: Thanh toan POS. Thoi gian: 06/10/2026 14:30.
    """
    try:
        result = client.extract(email_text)
    except Exception as e:
        pytest.skip(f"Ollama daemon not reachable or model not responding: {e}")

    assert result is not None
    assert result.get("bank_code") == "VIB"
    assert int(result.get("amount", 0)) == 75000
    assert result.get("transaction_type") == "DEBIT"
    assert "Highlands" in result.get("counterparty", "")
