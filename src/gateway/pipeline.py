import uuid
from typing import Any

from pydantic import BaseModel

from gateway.egress.cashflow_client import CashflowClient
from gateway.egress.viber_client import ViberClient, format_viber_alert_message
from gateway.extraction.guardrail import verify_verbatim_amount
from gateway.extraction.ollama_client import OllamaExtractionClient
from gateway.ingress.filter import is_bank_transaction_email
from gateway.ingress.mime_parser import parse_mime_email


class PipelineResult(BaseModel):
    processed: bool
    event_id: str | None = None
    skip_reason: str | None = None
    movement_status: str | None = None


class GatewayPipeline:
    def __init__(
        self,
        extractor: Any | None = None,
        cashflow_client: Any | None = None,
        viber_client: Any | None = None,
    ) -> None:
        self.extractor = extractor or OllamaExtractionClient()
        self.cashflow_client = cashflow_client or CashflowClient()
        self.viber_client = viber_client or ViberClient()

    def process_raw_email(self, raw_bytes: bytes) -> PipelineResult:
        # Step 1: Parse MIME
        email = parse_mime_email(raw_bytes)

        # Step 2: Heuristic Pre-filter
        if not is_bank_transaction_email(email):
            return PipelineResult(processed=False, skip_reason="NOT_BANK_ALERT")

        # Step 3: LLM Extraction
        extracted: dict[str, Any] = self.extractor.extract(email.body_text)

        # Step 4: Deterministic Guardrail
        verify_verbatim_amount(amount=extracted["amount"], body=email.body_text)

        # Step 5: Canonical Contract Event Construction
        event_id = str(uuid.uuid4())
        event_payload = {
            "event_id": event_id,
            "occurred_at": email.occurred_at.isoformat(),
            "bank_code": extracted.get("bank_code", "VIB"),
            "account_number_mask": extracted.get("account_number_mask"),
            "transaction_type": extracted.get("transaction_type", "DEBIT"),
            "amount": extracted["amount"],
            "currency": extracted.get("currency", "VND"),
            "remaining_balance": extracted.get("remaining_balance"),
            "description": extracted.get("description", email.subject),
            "counterparty": extracted.get("counterparty"),
            "category": extracted.get("category"),
            "raw_source_ref": email.message_id or f"RAW-{event_id}",
        }

        # Step 6: Post to Downstream Cashflow Core
        cashflow_res = self.cashflow_client.post_movement(event_payload)
        movement_status = cashflow_res.get("status", "UNKNOWN")

        # Step 7: Push Viber Alert (if new movement)
        if movement_status == "RECORDED":
            message = format_viber_alert_message(event_payload)
            self.viber_client.send_alert(message)

        return PipelineResult(
            processed=True,
            event_id=event_id,
            movement_status=movement_status,
        )
