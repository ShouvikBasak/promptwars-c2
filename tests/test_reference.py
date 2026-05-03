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

def test_firestore_fetch_error(api_client):
    """
    Verify local fallback when Firestore fetch raises an exception.
    """
    from backend.main import store
    mock_db = MagicMock()
    # Mock collection to raise error
    mock_db.collection.side_effect = Exception("Fetch Error")
    
    original_db = store.db
    try:
        with patch("backend.reference_store.FIRESTORE_ENABLED", True):
            store.db = mock_db
            # Should fall back to local "evm" entry
            response = api_client.get("/api/reference?key=evm")
            assert response.status_code == 200
            assert response.json()["title"] == "Electronic Voting Machine (EVM)"
    finally:
        store.db = original_db

def test_firestore_list_error(api_client):
    """
    Verify local fallback when Firestore listing raises an exception.
    """
    from backend.main import store
    mock_db = MagicMock()
    mock_db.collection.side_effect = Exception("List Error")
    
    original_db = store.db
    try:
        with patch("backend.reference_store.FIRESTORE_ENABLED", True):
            store.db = mock_db
            # Should fall back to local keys
            response = api_client.get("/api/reference")
            assert response.status_code == 200
            assert "evm" in response.json()["keys"]
    finally:
        store.db = original_db

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
