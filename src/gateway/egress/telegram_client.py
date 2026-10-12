import os
from typing import Any

import httpx


def format_telegram_alert_message(event: dict[str, Any]) -> str:
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


class TelegramClient:
    def __init__(
        self,
        bot_token: str | None = None,
        default_chat_id: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.bot_token = (
            bot_token if bot_token is not None else os.getenv("TELEGRAM_BOT_TOKEN", "")
        )
        self.default_chat_id = (
            default_chat_id
            if default_chat_id is not None
            else os.getenv("TELEGRAM_CHAT_ID", "")
        )
        self.timeout = timeout

    def send_alert(self, message: str, chat_id: str | None = None) -> bool:
        target_chat_id = chat_id or self.default_chat_id
        if not self.bot_token or not target_chat_id:
            # Dry-run / mock mode when credentials not configured
            return True

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": target_chat_id,
            "text": message,
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return bool(data.get("ok", False))
