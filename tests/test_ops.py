import pytest
import json

def test_health_endpoint(api_client):
    """Verify that the health endpoint is active and returns the expected status."""
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "timestamp" in response.json()

def test_observability_middleware_request_id(api_client, mock_vertex_client):
    """Verify that the middleware injects a Request-ID header."""
    response = api_client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0

def test_logging_safety_no_message_leakage(api_client, mock_vertex_client, capsys):
    """
    Verify that structured logs do not contain the raw user message.
    We check the captured stdout for the JSON log.
    """
    test_message = "SECRET_USER_INPUT_DO_NOT_LOG"
    api_client.post("/api/chat", json={"message": test_message})
    
    captured = capsys.readouterr()
    logs = captured.out.splitlines()
    
    found_log = False
    for line in logs:
        try:
            log_data = json.loads(line)
            if log_data.get("path") == "/api/chat":
                found_log = True
                # Critical Safety Check: The user message must NOT be in the log attributes
                assert test_message not in line, "User message found in structured logs!"
                assert "message" in log_data
                # The 'message' field should be a summary, not the raw input
                assert test_message not in log_data["message"]
        except json.JSONDecodeError:
            continue
    
    assert found_log, "Structured log for /api/chat was not found in stdout"

def test_error_reporting_middleware_resilience(api_client, capsys):
    """
    Verify that an unhandled exception bubbling to the middleware 
    triggers a structured error log and returns a safe 500.
    """
    response = api_client.get("/_crash_test")
    
    assert response.status_code == 500
    assert response.json()["error"] == "Internal Server Error"
    assert "request_id" in response.json()
    
    captured = capsys.readouterr()
    logs = captured.out.splitlines()
    
    found_error = False
    for line in logs:
        try:
            log_data = json.loads(line)
            if log_data.get("severity") == "ERROR":
                found_error = True
                assert "exception" in log_data
                assert "Intentional crash" in log_data["exception"]
                assert "serviceContext" in log_data
        except json.JSONDecodeError:
            continue
            
    assert found_error, "Structured error log was not found in stdout"

def test_chat_internal_resilience_logging(api_client, mock_vertex_client, capsys):
    """
    Verify that the chat endpoint's own catch-all block logs correctly 
    while returning a 200 OK safe refusal.
    """
    mock_vertex_client.models.generate_content.side_effect = Exception("Vertex AI Internal Error")
    
    response = api_client.post("/api/chat", json={"message": "Safe query"})
    
    assert response.status_code == 200
    assert "Election Commission of India sources" in response.json()["response"]
    
    captured = capsys.readouterr()
    logs = captured.out.splitlines()
    
    found_error = False
    for line in logs:
        try:
            log_data = json.loads(line)
            if log_data.get("severity") == "ERROR" and "Resilience catch-all" in log_data.get("message", ""):
                found_error = True
                assert "Vertex AI Internal Error" in log_data["exception"]
        except json.JSONDecodeError:
            continue
            
    assert found_error, "Structured error log from chat resilience block was not found"
