import asyncio
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from gateway.egress.cashflow_client import CashflowClient
from gateway.egress.telegram_client import TelegramClient
from gateway.extraction.ollama_client import OllamaExtractionClient
from gateway.pipeline import GatewayPipeline


def create_app() -> FastAPI:
    app = FastAPI(title="Stratum Perimeter Gateway", version="0.1.0")

    cashflow_url = os.getenv("CASHFLOW_API_URL", "http://localhost:8001")
    ollama_url = os.getenv("OLLAMA_HOST_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "qwen3.6:27b")

    extractor = OllamaExtractionClient(host_url=ollama_url, model=ollama_model)
    cashflow_client = CashflowClient(base_url=cashflow_url)
    notification_client = TelegramClient()

    pipeline = GatewayPipeline(
        extractor=extractor,
        cashflow_client=cashflow_client,
        notification_client=notification_client,
    )
    app.state.pipeline = pipeline

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/v1/ingest/email")
    async def ingest_email(request: Request, dispatch_alert: bool = True) -> JSONResponse:
        raw_bytes = await request.body()
        active_pipeline: GatewayPipeline = getattr(request.app.state, "pipeline", pipeline)
        result = await asyncio.to_thread(
            active_pipeline.process_raw_email, raw_bytes, dispatch_alert
        )
        return JSONResponse(status_code=200, content=result.model_dump())

    @app.post("/api/v1/batch/simulate")
    def simulate_batch(request: Request) -> JSONResponse:
        # Load sample VIB email from changes/fixtures
        fixture_path = (
            Path(__file__).parent.parent.parent
            / "changes"
            / "CR-26j001-bank-cashflow-ingestion"
            / "fixtures"
            / "sample_vib_debit.eml"
        )
        if not fixture_path.exists():
            # Fallback relative to current dir
            fixture_path = Path(
                "changes/CR-26j001-bank-cashflow-ingestion/fixtures/sample_vib_debit.eml"
            )

        with open(fixture_path, "rb") as f:
            raw_bytes = f.read()

        active_pipeline: GatewayPipeline = getattr(request.app.state, "pipeline", pipeline)
        result = active_pipeline.process_raw_email(raw_bytes)
        return JSONResponse(status_code=200, content=result.model_dump())

    return app
