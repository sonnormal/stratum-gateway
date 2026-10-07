import json
from typing import Any, cast

import httpx

EXTRACTION_PROMPT = (
    "You are a financial document parser. Extract bank alert details from the text below "
    "into pure JSON with keys: bank_code (e.g. VIB), account_number_mask (e.g. *4321), "
    "transaction_type (strictly either DEBIT or CREDIT), amount (positive number), "
    "currency (e.g. VND), description, counterparty, category."
)


def extract_json_payload(raw_content: str) -> dict[str, Any]:
    content = raw_content.strip()
    if "```json" in content:
        content = content.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in content:
        content = content.split("```", 1)[1].split("```", 1)[0].strip()
    return cast(dict[str, Any], json.loads(content))


class OllamaExtractionClient:
    def __init__(
        self,
        host_url: str = "http://localhost:11434",
        model: str = "qwen3.6:27b",
        timeout: float = 300.0,
    ) -> None:
        self.host_url = host_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def extract(self, body_text: str) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": body_text},
            ],
            "stream": False,
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.host_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "{}")
            return extract_json_payload(content)
