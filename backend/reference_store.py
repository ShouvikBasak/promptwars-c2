import os
import json
import logging
from google.cloud import firestore

# Setup logging
logger = logging.getLogger("elected-india-reference")

# Configuration
FIRESTORE_ENABLED = os.environ.get("FIRESTORE_ENABLED", "false").lower() == "true"
COLLECTION_NAME = "eci_reference"
LOCAL_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "eci_reference.json")

class ReferenceStore:
    def __init__(self):
        self.db = None
        self._local_cache = {}
        self._load_local_data()
        
        if FIRESTORE_ENABLED:
            try:
                # Firestore client uses Application Default Credentials (ADC)
                self.db = firestore.Client()
                logger.info("Firestore client initialized for reference store.")
            except Exception as e:
                logger.warning(f"Failed to initialize Firestore client: {e}. Falling back to local data.")

    def _load_local_data(self):
        try:
            if os.path.exists(LOCAL_DATA_PATH):
                with open(LOCAL_DATA_PATH, "r") as f:
                    self._local_cache = json.load(f)
                logger.info(f"Loaded {len(self._local_cache)} local reference entries.")
            else:
                logger.warning(f"Local reference data not found at {LOCAL_DATA_PATH}")
        except Exception as e:
            logger.error(f"Error loading local reference data: {e}")

    def get_reference(self, key):
        """
        Fetch a single reference entry by key.
        Priority: Firestore (if enabled) -> Local Cache.
        """
        if FIRESTORE_ENABLED and self.db:
            try:
                doc_ref = self.db.collection(COLLECTION_NAME).document(key)
                doc = doc_ref.get()
                if doc.exists:
                    return doc.to_dict()
            except Exception as e:
                logger.warning(f"Firestore fetch failed for key '{key}': {e}. Using local fallback.")
        
        return self._local_cache.get(key)

    def list_reference_keys(self):
        """
        List all available reference keys.
        Priority: Firestore (if enabled) -> Local Cache.
        """
        if FIRESTORE_ENABLED and self.db:
            try:
                docs = self.db.collection(COLLECTION_NAME).stream()
                keys = [doc.id for doc in docs]
                if keys:
                    return keys
            except Exception as e:
                logger.warning(f"Firestore list failed: {e}. Using local fallback.")
        
        return list(self._local_cache.keys())

# Singleton instance
store = ReferenceStore()
