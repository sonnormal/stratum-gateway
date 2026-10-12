import os
from typing import Any

import httpx


def format_viber_alert_message(event: dict[str, Any]) -> str:
    bank_code = event.get("bank_code", "BANK")
    txn_type = event.get("transaction_type", "DEBIT")
    amount = event.get("amount", 0)
    currency = event.get("currency", "VND")
    counterparty = event.get("counterparty", "N/A")
    category = event.get("category", "General")

    sign = "-" if txn_type == "DEBIT" else "+"
    try:
        formatted_amount = f"{int(amount):,}"
    except (ValueError, TypeError):
        formatted_amount = str(amount)

    return (
        f"[{bank_code}] Biến động: {sign}{formatted_amount} {currency} | "
        f"{counterparty} | Danh mục: {category}"
    )


class ViberClient:
    def __init__(
        self,
        auth_token: str | None = None,
        default_receiver: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.auth_token = auth_token if auth_token is not None else os.getenv("VIBER_AUTH_TOKEN", "")
        self.default_receiver = (
            default_receiver
            if default_receiver is not None
            else os.getenv("VIBER_RECEIVER_ID", os.getenv("VIBER_RECEIVER", "+84981801931"))
        )
        self.timeout = timeout

    def send_alert(self, message: str, receiver_id: str | None = None) -> bool:
        receiver = receiver_id or self.default_receiver
        if not self.auth_token:
            # Local mock / dry-run mode
            return True

        payload = {
            "receiver": receiver,
            "min_api_version": 1,
            "type": "text",
            "text": message,
        }
        headers = {"X-Viber-Auth-Token": self.auth_token}

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                "https://chatapi.viber.com/pa/send_message",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return bool(data.get("status") == 0)
