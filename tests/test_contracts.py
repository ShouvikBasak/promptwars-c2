import pytest
from unittest.mock import MagicMock

def test_api_contract_invariants(api_client, mock_vertex_client):
    """
    Assert that every successful API call returns the expected contract:
    - 200 OK
    - JSON with "response" key
    - "response" is a non-empty string
    """
    response = api_client.post("/api/chat", json={"message": "What is an EVM?"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0

def test_deterministic_refusal_string(api_client, mock_vertex_client):
    """
    Assert that out-of-scope queries return the EXACT refusal string.
    """
    mock_intent_response = MagicMock()
    mock_intent_response.text = '{"scope": "OUT_OF_SCOPE", "action": "REFUSE"}'
    mock_vertex_client.models.generate_content.return_value = mock_intent_response
    
    response = api_client.post("/api/chat", json={"message": "Who will win?"})
    expected = "This information is not available in official Election Commission of India sources."
    assert response.json()["response"] == expected

def test_no_pii_in_request_schema():
    """
    Assert that the ChatRequest schema contains no PII fields.
    """
    from backend.main import ChatRequest
    # Support both Pydantic v1 and v2
    if hasattr(ChatRequest, "model_fields"):
        fields = ChatRequest.model_fields.keys()
    else:
        fields = ChatRequest.__fields__.keys()
        
    prohibited = {"name", "email", "phone", "voter_id", "address", "epic", "ssn", "passport"}
    for field in prohibited:
        assert field not in fields, f"Prohibited PII field '{field}' found in ChatRequest schema"

def test_history_handling_contract(api_client, mock_vertex_client):
    """
    Assert that provided history is correctly passed to the model session creator.
    """
    history = [
        {"role": "user", "parts": [{"text": "Hello"}]},
        {"role": "model", "parts": [{"text": "Hi"}]}
    ]
    api_client.post("/api/chat", json={"message": "Tell me more", "history": history})
    
    assert mock_vertex_client.chats.create.called
    kwargs = mock_vertex_client.chats.create.call_args.kwargs
    assert "history" in kwargs
    assert len(kwargs["history"]) == 2

def test_regression_lock_no_internal_leakage(api_client, mock_vertex_client):
    """
    REGRESSION LOCK: Ensure the API never leaks internal errors or stack traces.
    Even if the backend logic throws an unhandled exception, the resilience 
    layer must catch it and return the deterministic refusal.
    """
    # Trigger a crash in the heart of the logic
    mock_vertex_client.models.generate_content.side_effect = RuntimeError("INTERNAL_SERVER_CRASH_TEST")
    
    response = api_client.post("/api/chat", json={"message": "Safe query"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "This information is not available in official Election Commission of India sources."
    # Absolute guarantee: no stack trace or internal error message in the response
    assert "RuntimeError" not in data["response"]
    assert "INTERNAL_SERVER_CRASH_TEST" not in data["response"]
    assert "traceback" not in str(data).lower()
