# 🌐 Stratum Perimeter Gateway (`gateway`)

> **Domain:** Omnichannel Perimeter Edge (Ingress & Egress)  
> **Runtime:** Python 3.12+ / FastAPI  
> **Status:** `ACTIVE` (TDD Phase 2 - `Green`)

---

## 📌 Responsibilities
* Ingests bank transaction emails (IMAP SSL / RFC 5322 MIME parsing).
* Filters non-bank and promotional emails using fast heuristic rules (< 1ms).
* Extracts structured transaction data via host Ollama LLM (`qwen3.6` / `qwen2.5`) with JSON schema constrained decoding.
* Enforces deterministic verbatim amount guardrails to prevent LLM hallucinations.
* Forwards validated `TransactionDetectedEvent` (v1) payloads to `services/cashflow:8001`.
* Formats and delivers real-time push alerts to stakeholder via Viber Bot API.

---

## 🧪 Testing & Verification
```bash
# Activate virtual environment
source .venv/bin/activate

# Run Tier 1 (Unit) and Tier 2 (Integration) tests
PYTHONPATH=src pytest
```
