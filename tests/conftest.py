import json
from pathlib import Path
from typing import Any, cast

import pytest

FIXTURES_DIR = (
    Path(__file__).parent.parent / "changes" / "CR-26j001-bank-cashflow-ingestion" / "fixtures"
)


@pytest.fixture
def sample_vib_email_bytes() -> bytes:
    with open(FIXTURES_DIR / "sample_vib_debit.eml", "rb") as f:
        return f.read()


@pytest.fixture
def sample_non_bank_email_bytes() -> bytes:
    with open(FIXTURES_DIR / "sample_non_bank.eml", "rb") as f:
        return f.read()


@pytest.fixture
def mock_ollama_extraction() -> dict[str, Any]:
    with open(FIXTURES_DIR / "mock_ollama_extraction.json") as f:
        return cast(dict[str, Any], json.load(f))
