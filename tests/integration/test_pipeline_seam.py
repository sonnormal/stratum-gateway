from typing import Any
from unittest.mock import MagicMock

from gateway.pipeline import GatewayPipeline


def test_pipeline_e2e_successful_ingestion(
    sample_vib_email_bytes: bytes, mock_ollama_extraction: dict[str, Any]
) -> None:
    mock_extractor = MagicMock()
    mock_extractor.extract.return_value = mock_ollama_extraction

    mock_cashflow_client = MagicMock()
    mock_cashflow_client.post_movement.return_value = {
        "status": "RECORDED",
        "movement_id": "test-uuid",
    }

    mock_viber_client = MagicMock()
    mock_viber_client.send_alert.return_value = True

    pipeline = GatewayPipeline(
        extractor=mock_extractor,
        cashflow_client=mock_cashflow_client,
        viber_client=mock_viber_client,
    )

    result = pipeline.process_raw_email(sample_vib_email_bytes)

    assert result.processed is True
    assert result.event_id is not None
    mock_extractor.extract.assert_called_once()
    mock_cashflow_client.post_movement.assert_called_once()
    mock_viber_client.send_alert.assert_called_once()


def test_pipeline_skips_non_bank_email(sample_non_bank_email_bytes: bytes) -> None:
    mock_extractor = MagicMock()
    mock_cashflow_client = MagicMock()
    mock_viber_client = MagicMock()

    pipeline = GatewayPipeline(
        extractor=mock_extractor,
        cashflow_client=mock_cashflow_client,
        viber_client=mock_viber_client,
    )

    result = pipeline.process_raw_email(sample_non_bank_email_bytes)

    assert result.processed is False
    assert result.skip_reason == "NOT_BANK_ALERT"
    mock_extractor.extract.assert_not_called()
    mock_cashflow_client.post_movement.assert_not_called()
    mock_viber_client.send_alert.assert_not_called()
