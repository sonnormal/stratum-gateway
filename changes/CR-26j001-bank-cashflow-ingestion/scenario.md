# 🧪 Stratum Repository Specification & Test Scenarios: gateway

> **Document Type:** Repo-Specific Technical Specification & Executable Acceptance Tests (`STEP-04` Red Phase)  
> **Target Checkpoint:** `GATE-02` (Contract & Test Scenario Gate)  
> **Location:** `gateway/changes/CR-26j001-bank-cashflow-ingestion/scenario.md`  
> **Scope:** Strictly isolated to `gateway` for **Technical Design**, **Tier 1 (Unit Tests)**, and **Tier 2 (Integration Tests)**. Tagged per the **Delta Principle**.

---

## 📌 1. Target Repository Metadata

| Field | Detail |
| :--- | :--- |
| **Change ID** | `CR-26j001` |
| **Target Repository** | [`gateway`](../../) |
| **Feature Fulfillments** | [FEAT-001: Bank Transaction Ingestion & Cashflow Alerting](../../../stratum-meta/features/vib-transaction-alert.md) |
| **Associated Flow** | [FLOW-001: Inbound Email Transaction Ingestion & Alerting](../../../stratum-meta/flows/email-transaction-ingestion.md) |
| **Bound Contracts** | [TransactionDetectedEvent (v1)](../../../stratum-meta/contracts/events/transaction_detected.v1.json) |
| **Author** | AI Verification Architect |
| **Status** | `RED_IN_PROGRESS` |
| **Master CR Record** | [CR-26j001 Evaluation Report](../../../stratum-meta/changes/CR-26j001-bank-cashflow-ingestion/evaluation.md) |

---

## 📐 2. Technical Scope & Implementation Invariants

### 2.1 Modules & Components to Create
* **`src/gateway/ingress/mime_parser.py`:** RFC 5322 MIME email parser extracting `sender`, `subject`, `date`, `message_id`, and `body_text`.
* **`src/gateway/ingress/filter.py`:** Fast heuristic filter discarding non-transaction and promotional emails in < 1ms before invoking LLM.
* **`src/gateway/extraction/ollama_client.py`:** Client interacting with host Ollama engine (`http://localhost:11434` / `http://host.docker.internal:11434`) with JSON schema constrained decoding.
* **`src/gateway/extraction/guardrail.py`:** Deterministic validator verifying that the extracted monetary amount exists verbatim in the raw email body before publishing.
* **`src/gateway/egress/cashflow_client.py`:** HTTP client forwarding `TransactionDetectedEvent` (v1) to downstream `services/cashflow:8001/api/v1/movements`.
* **`src/gateway/egress/viber_client.py`:** Formatter and webhook client for Viber Bot messaging to `+84981801931`.
* **`src/gateway/pipeline.py`:** Ingestion pipeline orchestrating Ingress → Filter → Extract → Guardrail → Cashflow → Viber.

### 2.2 Security & Operational Invariants
* **Zero External Cloud Inference:** LLM extraction executes strictly on host Apple Silicon Metal GPU via Ollama.
* **Verbatim Guardrail Invariant:** Any mismatch between LLM numeric amount and email body text raises `GuardrailViolationError` and halts event emission.
* **Account Masking:** Bank account numbers are masked (`*4321`) across all logs and notifications.

---

## 🔬 3. Tier 1: Unit Test Scenarios (In-Memory Isolation)

*Zero network, zero disk I/O. Execution budget < 10ms.*

### Scenario 1.1 [NEW]: MIME Email Parsing
* **Given:** A valid RFC 5322 email string matching `sample_vib_debit.eml`.
* **When:** `parse_mime_email(raw_bytes)` is executed.
* **Then:** Correctly extracts `message_id`, `sender = alert@vib.com.vn`, `subject`, `occurred_at`, and plain text body.

### Scenario 1.2 [NEW]: Heuristic Bank Email Filter
* **Given:** Parsed email objects.
* **When:** `is_bank_transaction_email(email)` is evaluated.
* **Then:** Returns `True` for VIB transaction email; returns `False` for promotional newsletters.

### Scenario 1.3 [NEW]: Verbatim Amount Guardrail Verification
* **Given:** Raw email text containing `"So tien: -75,000 VND"` and extracted amount `75000`.
* **When:** `verify_verbatim_amount(amount=75000, body=raw_text)` is executed.
* **Then:** Passes validation cleanly.

### Scenario 1.4 [NEW]: Guardrail Detects Hallucinated Amount
* **Given:** Raw email text containing `"So tien: -75,000 VND"` and hallucinated amount `99000`.
* **When:** `verify_verbatim_amount(amount=99000, body=raw_text)` is executed.
* **Then:** Raises `GuardrailViolationError` with clear mismatch detail.

### Scenario 1.5 [NEW]: Viber Alert Message Formatting
* **Given:** A validated `TransactionDetectedEvent` payload.
* **When:** `format_viber_message(event)` is called.
* **Then:** Formats a concise message for Viber: `[VIB] Bien dong: -75,000 VND | Highlands Coffee | Danh muc: Food & Beverage`.

---

## 🔌 4. Tier 2: Integration Test Scenarios (Container & Host Seams)

### Scenario 2.1 [NEW]: Ollama Host Bridge Extraction
* **Given:** The host Ollama daemon running at `http://localhost:11434`.
* **When:** `OllamaExtractionClient.extract(body_text)` is invoked.
* **Then:** Returns structured JSON matching required fields (`bank_code`, `amount`, `transaction_type`, `counterparty`, `category`).

### Scenario 2.2 [NEW]: End-to-End Pipeline Execution (Mocked Downstream)
* **Given:** A raw `.eml` file ingested through the `GatewayPipeline`.
* **When:** Downstream `cashflow` client and `viber` client are mocked.
* **Then:** The pipeline parses, extracts, verifies guardrail, posts movement to cashflow, and dispatches Viber notification.

---

## 📂 5. Test Fixtures Inventory (`fixtures/`)

| Fixture File | Type | Used In Scenario | Description |
| :--- | :--- | :--- | :--- |
| `fixtures/sample_vib_debit.eml` | RFC 5322 MIME | Scenario 1.1, 1.2, 2.2 | Real-world VIB POS debit email |
| `fixtures/sample_non_bank.eml` | RFC 5322 MIME | Scenario 1.2 | Promotional newsletter email |
| `fixtures/mock_ollama_extraction.json` | JSON | Scenario 1.5, 2.2 | Mocked structured LLM extraction response |

---

## ⚖️ 6. GATE-02 Verification Checklist

- [x] Technical scope strictly isolated to `gateway` repository boundaries.
- [x] Tier 1 tests run in-memory (< 10ms) with zero I/O (6 passed in 0.07s).
- [x] Tier 2 tests verify the Ollama bridge and pipeline integration.
- [x] All fixtures sanitized (zero real passwords or personal tokens).
- [x] Automated tests verified in `Green` state with `ruff` and `mypy --strict` passing with 0 warnings.
- [x] Verification Status: `GREEN_PASSED` (Ready for end-to-end container integration).
