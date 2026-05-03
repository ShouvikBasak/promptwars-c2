import pytest
from unittest.mock import MagicMock

def test_vertex_intent_exception_handling(api_client, mock_vertex_client):
    """
    Test that an exception in the Intent Classification Vertex call 
    does not leak stack traces and returns a safe refusal.
    """
    mock_vertex_client.models.generate_content.side_effect = Exception("Vertex Connectivity Error")
    
    response = api_client.post("/api/chat", json={"message": "What is an EVM?"})
    # If this fails with 500, it means the app isn't resilient to this failure.
    # Architecture requirements prefer 200 with REFUSAL_MESSAGE for safe degradation.
    assert response.status_code == 200
    assert response.json()["response"] == "This information is not available in official Election Commission of India sources."

def test_vertex_answer_exception_handling(api_client, mock_vertex_client):
    """
    Test that an exception during Answer Generation returns a safe refusal.
    """
    # Intent classification succeeds
    mock_intent_response = MagicMock()
    mock_intent_response.text = '{"scope": "IN_SCOPE", "action": "ANSWER"}'
    mock_vertex_client.models.generate_content.return_value = mock_intent_response
    
    # Answer generation fails
    mock_chat_session = mock_vertex_client.chats.create.return_value
    mock_chat_session.send_message.side_effect = Exception("Generation Timeout")
    
    response = api_client.post("/api/chat", json={"message": "How do I vote?"})
    assert response.status_code == 200
    assert response.json()["response"] == "This information is not available in official Election Commission of India sources."

def test_model_returns_empty_or_none_text(api_client, mock_vertex_client):
    """
    Test resilience against empty response text from the model.
    """
    mock_intent_response = MagicMock()
    mock_intent_response.text = "" # Empty
    mock_vertex_client.models.generate_content.return_value = mock_intent_response
    
    response = api_client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 200
    assert response.json()["response"] == "This information is not available in official Election Commission of India sources."

def test_intent_json_missing_keys_resilience(api_client, mock_vertex_client):
    """
    Test that if the intent JSON is valid but missing the 'action' key, we refuse.
    """
    mock_intent_response = MagicMock()
    mock_intent_response.text = '{"scope": "IN_SCOPE"}' # Missing 'action'
    mock_vertex_client.models.generate_content.return_value = mock_intent_response
    
    response = api_client.post("/api/chat", json={"message": "Register me"})
    assert response.status_code == 200
    assert response.json()["response"] == "This information is not available in official Election Commission of India sources."

def test_malformed_llm_response_object(api_client, mock_vertex_client):
    """
    Test resilience when the SDK response object is malformed (e.g. missing .text attribute).
    """
    # Create an object that doesn't have a .text attribute
    mock_intent_response = MagicMock(spec=[]) 
    mock_vertex_client.models.generate_content.return_value = mock_intent_response
    
    response = api_client.post("/api/chat", json={"message": "What is EVM?"})
    assert response.status_code == 200
    assert response.json()["response"] == "This information is not available in official Election Commission of India sources."

def test_chats_create_exception(api_client, mock_vertex_client):
    """
    Test resilience when client.chats.create raises an exception.
    """
    # Intent classification succeeds
    mock_intent_response = MagicMock()
    mock_intent_response.text = '{"scope": "IN_SCOPE", "action": "ANSWER"}'
    mock_vertex_client.models.generate_content.return_value = mock_intent_response
    
    # chats.create fails
    mock_vertex_client.chats.create.side_effect = Exception("Chat session creation failed")
    
    response = api_client.post("/api/chat", json={"message": "How do I vote?"})
    assert response.status_code == 200
    assert response.json()["response"] == "This information is not available in official Election Commission of India sources."

def test_intent_none_text_attribute(api_client, mock_vertex_client):
    """
    Test resilience when the response object exists but .text is explicitly None.
    """
    mock_intent_response = MagicMock()
    mock_intent_response.text = None
    mock_vertex_client.models.generate_content.return_value = mock_intent_response
    
    response = api_client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 200
    assert response.json()["response"] == "This information is not available in official Election Commission of India sources."
