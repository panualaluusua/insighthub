"""
Vector Store Abstraction Layer for persisting user & content vectors.
Defaults to an in-memory implementation but can switch to Supabase Postgres
(backed by pgvector) if SUPABASE_URL & SUPABASE_SERVICE_KEY env vars are set.
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional
import numpy as np

# Optional import – handled gracefully if supabase-py not installed
try:
    from supabase import create_client, Client  # type: ignore
except ImportError:  # pragma: no cover
    Client = None  # type: ignore


class VectorStore:
    """Abstract base class for vector storage backends."""

    # --- Content vectors -------------------------------------------------
    def get_content_vector(self, content_id: str, dimension: int = 1536) -> np.ndarray:  # noqa: D401
        raise NotImplementedError

    def save_content_vector(self, content_id: str, vector: np.ndarray) -> None:  # noqa: D401
        raise NotImplementedError

    # --- User vectors ----------------------------------------------------
    def get_user_vector(self, user_id: str, dimension: int = 1536) -> np.ndarray:  # noqa: D401
        raise NotImplementedError

    def save_user_vector(self, user_id: str, vector: np.ndarray) -> None:  # noqa: D401
        raise NotImplementedError


class InMemoryVectorStore(VectorStore):
    """Simple Python-dict backed store – handy for local dev & tests."""

    def __init__(self):
        self._content: Dict[str, np.ndarray] = {}
        self._users: Dict[str, np.ndarray] = {}

    # --- helpers --------------------------------------------------------
    def _init_vec(self, key: str, store: Dict[str, np.ndarray], dimension: int) -> np.ndarray:
        if key not in store:
            store[key] = np.zeros(dimension, dtype=np.float32)
        return store[key]

    # --- content --------------------------------------------------------
    def get_content_vector(self, content_id: str, dimension: int = 1536) -> np.ndarray:  # noqa: D401
        return self._init_vec(content_id, self._content, dimension)

    def save_content_vector(self, content_id: str, vector: np.ndarray) -> None:  # noqa: D401
        self._content[content_id] = vector

    # --- users ----------------------------------------------------------
    def get_user_vector(self, user_id: str, dimension: int = 1536) -> np.ndarray:  # noqa: D401
        return self._init_vec(user_id, self._users, dimension)

    def save_user_vector(self, user_id: str, vector: np.ndarray) -> None:  # noqa: D401
        self._users[user_id] = vector


class SupabaseVectorStore(VectorStore):
    """Supabase Postgres implementation (requires pgvector extension)."""

    def __init__(self, url: str, key: str):
        if Client is None:
            raise RuntimeError("supabase-py not installed. `pip install supabase-py`.")
        self.client: Client = create_client(url, key)

    # --- utils ----------------------------------------------------------
    @staticmethod
    def _to_numpy(record) -> np.ndarray:
        if record is None or record["vector"] is None:
            return np.array([])
        vec = record["vector"].strip("[]")
        return np.fromstring(vec, sep=",", dtype=np.float32)

    @staticmethod
    def _to_pg(vec: np.ndarray) -> List[float]:
        return vec.astype(float).tolist()

    # --- content --------------------------------------------------------
    def get_content_vector(self, content_id: str, dimension: int = 1536) -> np.ndarray:  # noqa: D401
        resp = (
            self.client.table("content_vectors").select("vector").eq("id", content_id).execute()
        )
        if resp.data:
            return self._to_numpy(resp.data[0])
        return np.zeros(dimension, dtype=np.float32)

    def save_content_vector(self, content_id: str, vector: np.ndarray) -> None:  # noqa: D401
        payload = {"id": content_id, "vector": self._to_pg(vector)}
        self.client.table("content_vectors").upsert(payload).execute()

    # --- users ----------------------------------------------------------
    def get_user_vector(self, user_id: str, dimension: int = 1536) -> np.ndarray:  # noqa: D401
        resp = (
            self.client.table("user_vectors").select("vector").eq("user_id", user_id).execute()
        )
        if resp.data:
            return self._to_numpy(resp.data[0])
        return np.zeros(dimension, dtype=np.float32)

    def save_user_vector(self, user_id: str, vector: np.ndarray) -> None:  # noqa: D401
        payload = {"user_id": user_id, "vector": self._to_pg(vector)}
        self.client.table("user_vectors").upsert(payload).execute()


# -------------------------------------------------------------------------
# Factory / singleton pattern
# -------------------------------------------------------------------------
_store_instance: Optional[VectorStore] = None

def get_vector_store() -> VectorStore:  # noqa: D401
    """Return a singleton vector store backend based on env configuration."""
    global _store_instance
    if _store_instance is not None:
        return _store_instance

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

    if supabase_url and supabase_key:
        try:
            _store_instance = SupabaseVectorStore(supabase_url, supabase_key)
            return _store_instance
        except Exception:
            # Misconfiguration – gracefully fall back to memory store
            pass

    _store_instance = InMemoryVectorStore()
    return _store_instance 