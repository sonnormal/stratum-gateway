from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from gateway.main import create_app


def test_gateway_healthz() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_gateway_ingest_email_endpoint(sample_vib_email_bytes: bytes) -> None:
    app = create_app()

    # Mock the internal pipeline
    mock_pipeline = MagicMock()
    mock_pipeline.process_raw_email.return_value = MagicMock(
        model_dump=lambda: {
            "processed": True,
            "event_id": "mock-event",
            "movement_status": "RECORDED",
        }
    )
    app.state.pipeline = mock_pipeline

    client = TestClient(app)
    response = client.post("/api/v1/ingest/email", content=sample_vib_email_bytes)

    assert response.status_code == 200
    data = response.json()
    assert data["processed"] is True
    assert data["movement_status"] == "RECORDED"
