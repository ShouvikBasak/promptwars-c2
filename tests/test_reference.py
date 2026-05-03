import pytest
from unittest.mock import MagicMock, patch
import os
import json

def test_reference_local_fallback(api_client):
    """
    Verify that the reference store falls back to local JSON when Firestore is disabled.
    """
    # By default FIRESTORE_ENABLED is false in our environment
    response = api_client.get("/api/reference?key=evm")
    assert response.status_code == 200
    assert response.json()["title"] == "Electronic Voting Machine (EVM)"

def test_reference_list_keys(api_client):
    """
    Verify listing keys from local data.
    """
    response = api_client.get("/api/reference")
    assert response.status_code == 200
    assert "keys" in response.json()
    assert "evm" in response.json()["keys"]

def test_reference_not_found(api_client):
    """
    Verify 404 for non-existent keys.
    """
    response = api_client.get("/api/reference?key=non_existent")
    assert response.status_code == 404

def test_firestore_path_called_when_enabled(api_client):
    """
    Verify that Firestore path is exercised when enabled.
    """
    # Mock the collection/document/get chain
    mock_db = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"title": "Firestore Title"}
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Patch the singleton store instance in main.py
    from backend.main import store
    original_db = store.db
    original_enabled = store.db is not None
    
    try:
        # Manually inject mock and force enable
        with patch("backend.reference_store.FIRESTORE_ENABLED", True):
            store.db = mock_db
            response = api_client.get("/api/reference?key=evm")
            assert response.status_code == 200
            assert response.json()["title"] == "Firestore Title"
            assert mock_db.collection.called
    finally:
        # Restore
        store.db = original_db

def test_no_user_data_in_schema():
    """
    Verify that the reference data contains only static fields and no PII.
    """
    from backend.reference_store import store
    keys = store.list_reference_keys()
    for key in keys:
        entry = store.get_reference(key)
        # Check for any PII-like fields that shouldn't be there
        prohibited = {"user", "session", "message", "history", "email", "name", "voter_id"}
        for p in prohibited:
            assert p not in entry, f"Found prohibited field '{p}' in reference entry '{key}'"

def test_reference_local_data_not_found():
    """
    Verify behavior when local JSON file is missing.
    """
    from backend.reference_store import ReferenceStore
    with patch("os.path.exists", return_value=False):
        # This will trigger the logger.warning(Local reference data not found)
        store = ReferenceStore()
        assert store._local_cache == {}

def test_reference_load_error():
    """
    Verify behavior when local JSON file is malformed.
    """
    from backend.reference_store import ReferenceStore
    with patch("builtins.open", side_effect=Exception("Read Error")):
        # This will trigger the logger.error(Error loading local reference data)
        store = ReferenceStore()
        assert store._local_cache == {}

def test_firestore_init_error():
    """
    Verify behavior when Firestore client initialization fails.
    """
    from backend.reference_store import ReferenceStore
    with patch("google.cloud.firestore.Client", side_effect=Exception("Init Error")), \
         patch("backend.reference_store.FIRESTORE_ENABLED", True):
        store = ReferenceStore()
        assert store.db is None

def test_http_exception_in_route(api_client):
    """
    Trigger an HTTPException inside the route to cover the re-raise logic.
    """
    from fastapi import HTTPException
    with patch("backend.main.run_chat_logic", side_effect=HTTPException(status_code=400, detail="Bad request")):
        response = api_client.post("/api/chat", json={
            "message": "hello",
            "history": []
        })
        assert response.status_code == 400

def test_firestore_init_success():
    """
    Verify that Firestore client initialization logs success.
    """
    from backend.reference_store import ReferenceStore
    with patch("google.cloud.firestore.Client"), \
         patch("backend.reference_store.FIRESTORE_ENABLED", True):
        # We need to ensure the logger is at least INFO level
        with patch("backend.reference_store.logger.info") as mock_info:
            store = ReferenceStore()
            assert store.db is not None
            assert mock_info.called
            # Check for the specific message
            args, _ = mock_info.call_args
            assert "Firestore client initialized" in args[0]

def test_firestore_list_keys_success():
    """
    Verify successful listing of keys from Firestore mock.
    """
    from backend.reference_store import ReferenceStore
    mock_db = MagicMock()
    mock_doc = MagicMock()
    mock_doc.id = "fire_key"
    mock_db.collection.return_value.stream.return_value = [mock_doc]
    
    with patch("google.cloud.firestore.Client", return_value=mock_db), \
         patch("backend.reference_store.FIRESTORE_ENABLED", True):
        store = ReferenceStore()
        keys = store.list_reference_keys()
        assert "fire_key" in keys

def test_request_size_limit(api_client):
    """
    Verify that requests exceeding 100KB are rejected with 413.
    """
    large_message = "a" * 101_000
    payload = json.dumps({"message": large_message, "history": []})
    response = api_client.post("/api/chat", 
        content=payload,
        headers={
            "Content-Length": str(len(payload)),
            "Content-Type": "application/json"
        }
    )
    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()

def test_soft_timeout_handling(api_client):
    """
    Verify that soft timeout (25s) returns a safe refusal.
    """
    import asyncio
    from unittest.mock import AsyncMock
    
    # Mock run_chat_logic to be an async function
    with patch("backend.main.run_chat_logic", new_callable=AsyncMock) as mock_logic:
        with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError()):
            response = api_client.post("/api/chat", json={
                "message": "hello",
                "history": []
            })
            assert response.status_code == 200
            assert "This information is not available" in response.json()["response"]

def test_firestore_list_keys_cache_hit():
    """
    Verify cache hit in list_reference_keys.
    """
    from backend.reference_store import ReferenceStore
    mock_db = MagicMock()
    # First call will populate cache
    mock_doc = MagicMock()
    mock_doc.id = "key1"
    mock_db.collection.return_value.stream.return_value = [mock_doc]
    
    with patch("google.cloud.firestore.Client", return_value=mock_db), \
         patch("backend.reference_store.FIRESTORE_ENABLED", True):
        store = ReferenceStore()
        keys1 = store.list_reference_keys()
        assert keys1 == ["key1"]
        
        # Second call should not hit mock_db again
        mock_db.collection.return_value.stream.reset_mock()
        keys2 = store.list_reference_keys()
        assert keys2 == ["key1"]
        assert not mock_db.collection.return_value.stream.called

def test_firestore_fetch_cache_hit():
    """
    Verify cache hit in get_reference.
    """
    from backend.reference_store import ReferenceStore
    mock_db = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"val": 1}
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
    
    with patch("google.cloud.firestore.Client", return_value=mock_db), \
         patch("backend.reference_store.FIRESTORE_ENABLED", True):
        store = ReferenceStore()
        val1 = store.get_reference("k1")
        assert val1 == {"val": 1}
        
        # Second call should not hit mock_db again
        mock_db.collection.return_value.document.reset_mock()
        val2 = store.get_reference("k1")
        assert val2 == {"val": 1}
        assert not mock_db.collection.return_value.document.called

def test_resilience_catch_all_coverage(api_client):
    """
    Trigger the Resilience catch-all in the chat endpoint for coverage.
    """
    with patch("backend.main.run_chat_logic", side_effect=RuntimeError("Extreme failure")):
        response = api_client.post("/api/chat", json={
            "message": "hello",
            "history": []
        })
        assert response.status_code == 200
        assert "This information is not available" in response.json()["response"]

def test_firestore_fetch_error_logging():
    """
    Verify fallback and logging when Firestore fetch fails.
    """
    from backend.reference_store import store
    mock_db = MagicMock()
    # Mock collection().document().get() to raise an exception
    mock_db.collection.return_value.document.return_value.get.side_effect = Exception("Fetch error")
    
    original_db = store.db
    store.db = mock_db
    try:
        with patch("backend.reference_store.FIRESTORE_ENABLED", True), \
             patch("backend.reference_store.logger.warning") as mock_warn:
            # Force cache miss
            store._firestore_cache.clear()
            val = store.get_reference("evm")
            assert val is not None # Falls back to local
            assert mock_warn.called
            assert "Firestore fetch failed" in mock_warn.call_args[0][0]
    finally:
        store.db = original_db

def test_firestore_list_error_logging():
    """
    Verify fallback and logging when Firestore listing fails.
    """
    from backend.reference_store import store
    mock_db = MagicMock()
    # Mock collection().stream() to raise an exception
    mock_db.collection.return_value.stream.side_effect = Exception("List error")
    
    original_db = store.db
    store.db = mock_db
    try:
        with patch("backend.reference_store.FIRESTORE_ENABLED", True), \
             patch("backend.reference_store.logger.warning") as mock_warn:
            # Force cache miss
            store._firestore_cache.clear()
            keys = store.list_reference_keys()
            assert "evm" in keys # Falls back to local
            assert mock_warn.called
            assert "Firestore list failed" in mock_warn.call_args[0][0]
    finally:
        store.db = original_db

