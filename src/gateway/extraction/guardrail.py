from decimal import Decimal


class GuardrailViolationError(Exception):
    """Raised when an LLM extracted value fails verbatim body verification."""

    pass


def verify_verbatim_amount(amount: int | float | Decimal, body: str) -> None:
    """Verifies that the numeric amount extracted by the LLM appears verbatim in body."""
    numeric_val = int(amount)
    variants = [
        str(numeric_val),
        f"{numeric_val:,}",  # 75,000
        f"{numeric_val:,}".replace(",", "."),  # 75.000
        f"{numeric_val:,}".replace(",", " "),  # 75 000
    ]

    found = any(variant in body for variant in variants)
    if not found:
        raise GuardrailViolationError(f"Amount {amount} not found in email body")
