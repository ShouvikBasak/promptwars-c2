# Implementation Plan - Testing Uplift

Increase the "Testing" score by implementing a robust test suite for the FastAPI backend.

## User Review Required

> [!IMPORTANT]
> The test suite will use `pytest` and `httpx`. No changes to the application's core logic or prompts are planned, except for adding minimal hooks if monkeypatching proves insufficient.

## Proposed Changes

### [Backend Testing]

#### [NEW] [requirements-dev.txt](file:///Users/shouvik/myRepos/promptwars-c2/requirements-dev.txt)
Add development dependencies: `pytest`, `pytest-asyncio`, `pytest-cov`, `httpx`.

#### [NEW] [conftest.py](file:///Users/shouvik/myRepos/promptwars-c2/tests/conftest.py)
Configure pytest fixtures and a reusable mock for the `google.genai.Client`.

#### [NEW] [test_api.py](file:///Users/shouvik/myRepos/promptwars-c2/tests/test_api.py)
Implement the following test categories:
- **Core Path**: Successful in-scope question.
- **Refusal Path**: Out-of-scope question (e.g., political opinion).
- **Edge Cases**:
    - Empty question string.
    - Whitespace-only question.
    - Extremely long question.
    - Mixed-language / Special characters.
- **Negative Paths**:
    - Invalid JSON payload.
    - Missing required fields.
- **Integration/Failure Paths**:
    - Vertex AI classification failure (handled by a safe default in `main.py`).
    - Vertex AI answer generation failure.

#### [NEW] [run_tests.sh](file:///Users/shouvik/myRepos/promptwars-c2/scripts/run_tests.sh)
A helper script to run tests with coverage reporting.

### [Documentation]

#### [MODIFY] [README.md](file:///Users/shouvik/myRepos/promptwars-c2/README.md)
Add a "Testing" section with instructions on how to run the new test suite.

## Verification Plan

### Automated Tests
- Run `pytest` and ensure 100% pass rate.
- Check coverage report to ensure all critical paths in `backend/main.py` are exercised.

### Manual Verification
- None required from the user, as these are internal tests.
