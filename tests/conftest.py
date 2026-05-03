import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure the root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session", autouse=True)
def _mock_vertex_client_class():
    """
    Session-scoped patch of the genai.Client class to ensure no network calls occur.
    """
    with patch("google.genai.Client") as mock_class:
        yield mock_class

@pytest.fixture
def mock_vertex_client(_mock_vertex_client_class):
    """
    Provides the mocked client instance and sets up default successful responses.
    """
    mock_instance = _mock_vertex_client_class.return_value
    
    # --- Reset to default success state ---
    
    # 1. Intent Classification Mock
    mock_intent_response = MagicMock()
    mock_intent_response.text = '{"scope": "IN_SCOPE", "category": "ELECTION_PROCESS", "action": "ANSWER"}'
    mock_instance.models.generate_content.side_effect = None
    mock_instance.models.generate_content.return_value = mock_intent_response
    
    # 2. Answer Generation Mock
    mock_chat_session = MagicMock()
    mock_answer_response = MagicMock()
    mock_answer_response.text = "This is a mocked educational answer about elections."
    mock_instance.chats.create.return_value = mock_chat_session
    mock_chat_session.send_message.side_effect = None
    mock_chat_session.send_message.return_value = mock_answer_response
    
    return mock_instance

@pytest.fixture
def api_client(mock_vertex_client):
    """
    Returns a FastAPI TestClient with the mocked Vertex client injected.
    """
    from fastapi.testclient import TestClient
    import backend.main
    
    # Force injection of the current mock instance into the backend module
    backend.main.client = mock_vertex_client
    
    return TestClient(backend.main.app)
