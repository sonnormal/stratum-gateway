import os

import pytest

from gateway.extraction.ollama_client import OllamaExtractionClient


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("RUN_OLLAMA_INTEGRATION"),
    reason="Requires host Ollama daemon (set RUN_OLLAMA_INTEGRATION=1)",
)
def test_ollama_client_live_extraction() -> None:
    client = OllamaExtractionClient(
        host_url="http://localhost:11434",
        model="qwen3.6:27b",
        timeout=180.0,
    )
    email_text = """
    VIB Thong bao: Tai khoan *4321 vua phat sinh giao dich -75,000 VND tai Highlands Coffee.
    Loai GD: Thanh toan POS. Thoi gian: 06/10/2026 14:30.
    """
    try:
        result = client.extract(email_text)
    except Exception as e:
        pytest.skip(f"Ollama daemon not reachable or model not responding: {e}")

    assert result is not None
    assert int(result.get("amount", 0)) == 75000
    assert "Highlands" in str(result.get("counterparty", ""))
