"""
Distributed Session Persistence layer for Coffee Concierge.
Provides Firestore-backed session storage for high-availability multi-instance deployments.
"""

import os
import datetime
from typing import Optional, Dict, Any, List
from google.cloud import firestore

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-e7ff715cb28f")
COLLECTION_NAME = "agent_sessions"

class FirestoreSessionStore:
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or PROJECT_ID
        try:
            self.db = firestore.Client(project=self.project_id)
            self.available = True
        except Exception as e:
            print(f"Warning: Firestore session persistence disabled: {e}")
            self.db = None
            self.available = False

    def save_session(self, session_id: str, user_id: str, messages: List[Dict[str, Any]]) -> bool:
        """Persist conversation session history to Firestore."""
        if not self.available or not self.db:
            return False
        try:
            doc_ref = self.db.collection(COLLECTION_NAME).document(session_id)
            doc_ref.set({
                "session_id": session_id,
                "user_id": user_id,
                "messages": messages,
                "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }, merge=True)
            return True
        except Exception as e:
            print(f"Failed to persist session {session_id} to Firestore: {e}")
            return False

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve conversation session history from Firestore."""
        if not self.available or not self.db:
            return None
        try:
            doc_ref = self.db.collection(COLLECTION_NAME).document(session_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Failed to load session {session_id} from Firestore: {e}")
            return None

session_store = FirestoreSessionStore()
