# ElectEd India - Test Matrix

This document maps architectural guarantees and safety requirements to their corresponding test implementations.

| Guarantee Category | Requirement | Test Name(s) | File |
|--------------------|-------------|--------------|------|
| **Core Flow** | Valid educational queries return grounded answers | `test_chat_success` | `tests/test_api.py` |
| **Safety** | Out-of-scope queries (opinion, prediction) are refused | `test_chat_refusal`, `test_deterministic_refusal_string` | `tests/test_contracts.py` |
| **Safety** | Adversarial prompt injections are caught | `test_adversarial_refusal_gate` | `tests/test_adversarial.py` |
| **Safety** | No raw script/malicious tags are reflected | `test_chat_edge_cases`, `test_adversarial_refusal_gate` | `tests/test_api.py`, `tests/test_adversarial.py` |
| **Privacy** | No PII fields are accepted in the request schema | `test_no_pii_in_request_schema` | `tests/test_contracts.py` |
| **Resilience** | Vertex AI service exceptions return safe refusal | `test_vertex_intent_exception_handling`, `test_vertex_answer_exception_handling`, `test_chats_create_exception` | `tests/test_resilience.py` |
| **Resilience** | Malformed model responses handle safely | `test_chat_intent_parse_failure`, `test_model_returns_empty_or_none_text`, `test_malformed_llm_response_object` | `tests/test_resilience.py` |
| **Contract** | API responses always contain a non-empty string | `test_api_contract_invariants` | `tests/test_contracts.py` |
| **Contract** | Regression lock: No stack traces or internal leakages | `test_regression_lock_no_internal_leakage` | `tests/test_contracts.py` |
| **Architecture** | Chat history is correctly preserved for context | `test_history_handling_contract` | `tests/test_contracts.py` |

## Summary
- **Deterministic**: All tests use mocked Vertex AI.
- **Coverage Target**: 100% of backend orchestrator logic.
- **Automation**: Verified on every push via GitHub Actions.
