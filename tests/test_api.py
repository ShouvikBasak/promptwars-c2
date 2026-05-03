import pytest
import json
from unittest.mock import MagicMock

def test_chat_success(api_client, mock_vertex_client):
    """Test a successful in-scope educational query."""
    response = api_client.post("/api/chat", json={"message": "How do I register to vote?"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0
    assert "mocked educational answer" in data["response"]

def test_chat_refusal(api_client, mock_vertex_client):
    """Test that an out-of-scope query is refused with the deterministic string."""
    # Mock the intent classifier to return REFUSE
    mock_intent_response = MagicMock()
    mock_intent_response.text = '{"scope": "OUT_OF_SCOPE", "category": "POLITICAL_OPINION", "action": "REFUSE"}'
    mock_vertex_client.models.generate_content.return_value = mock_intent_response
    
    response = api_client.post("/api/chat", json={"message": "Who should I vote for?"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["response"] == "This information is not available in official Election Commission of India sources."

def test_chat_intent_parse_failure(api_client, mock_vertex_client):
    """Test that if the intent classifier returns garbage, we default to refusal."""
    mock_intent_response = MagicMock()
    mock_intent_response.text = "NOT JSON"
    mock_vertex_client.models.generate_content.return_value = mock_intent_response
    
    response = api_client.post("/api/chat", json={"message": "What is an EVM?"})
    assert response.status_code == 200
    assert response.json()["response"] == "This information is not available in official Election Commission of India sources."

@pytest.mark.parametrize("input_text", [
    "", # Empty
    "   ", # Whitespace
    "A" * 5000, # Long
    "नमस्ते! चुनाव कब हैं?", # Special characters/Unicode (Hindi)
    "<script>alert('injection')</script>", # Malicious-looking strings
])
def test_chat_edge_cases(api_client, mock_vertex_client, input_text):
    """
    Test various edge cases for the message input.
    Validates API contract, robustness, safety, and deterministic behavior.
    """
    # Ensure classification succeeds for edge cases so we test the full pipeline
    mock_intent_response = MagicMock()
    mock_intent_response.text = '{"scope": "IN_SCOPE", "category": "CIVIC_EDUCATION", "action": "ANSWER"}'
    mock_vertex_client.models.generate_content.return_value = mock_intent_response

    response = api_client.post("/api/chat", json={"message": input_text})
    
    # 1) API Contract Guarantees
    assert response.status_code == 200, f"Expected 200 OK for input: {input_text}"
    data = response.json()
    assert "response" in data, "JSON response must include 'response' field"
    assert isinstance(data["response"], str), "'response' field must be a string"

    # 2) Robustness Guarantees
    response_text = data["response"].strip()
    assert len(response_text) > 0, "Response should not be empty or whitespace-only"
    # Guard against sprawling responses (architectural bound)
    assert len(data["response"]) < 10000, "Response length exceeded reasonable architectural bounds"

    # 3) Safety Guarantees
    # Output must not echo raw injection content or reflect malicious input verbatim
    prohibited_snippets = ["<script>", "alert(", "javascript:"]
    for snippet in prohibited_snippets:
        assert snippet not in data["response"], f"Safety violation: response contains prohibited snippet '{snippet}'"
    
    # Ensure input reflection is bounded/prevented for safety
    if len(input_text.strip()) > 10:
        assert input_text not in data["response"], "Safety violation: input was reflected verbatim in the response"

def test_invalid_json_payload(api_client):
    """Test sending a non-JSON payload."""
    response = api_client.post("/api/chat", content="not json", headers={"Content-Type": "application/json"})
    assert response.status_code == 422 # FastAPI validation error

def test_missing_required_field(api_client):
    """Test sending a JSON payload missing the 'message' field."""
    response = api_client.post("/api/chat", json={"not_message": "hello"})
    assert response.status_code == 422
