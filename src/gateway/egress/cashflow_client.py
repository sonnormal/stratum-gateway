from typing import Any

import httpx


class CashflowClient:
    def __init__(self, base_url: str = "http://localhost:8001", timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def post_movement(self, event_payload: dict[str, Any]) -> dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/api/v1/movements",
                json=event_payload,
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            return data
