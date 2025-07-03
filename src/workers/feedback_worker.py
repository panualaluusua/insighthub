"""Feedback worker and queue utilities.
Uses Redis RQ when available, falls back to inline processing.
"""
from __future__ import annotations

import os
import logging
from typing import Dict, Any
import numpy as np

from src.models.vector_math import FeedbackType, UserProfileVectorManager
from src.storage.vector_store import get_vector_store

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Optional redis / rq imports
# ------------------------------------------------------------------
try:
    import redis  # type: ignore
    from rq import Queue, Worker  # type: ignore
except ImportError:  # pragma: no cover
    redis = None  # type: ignore
    Queue = None  # type: ignore

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def _get_queue():
    """Return an RQ queue instance or None if unavailable."""
    if redis is None or Queue is None:
        return None
    try:
        conn = redis.from_url(REDIS_URL)
        return Queue("feedback", connection=conn)
    except Exception as exc:  # pragma: no cover
        logger.warning("Redis unavailable (%s), falling back to inline", exc)
        return None


def enqueue_feedback_event(event: Dict[str, Any]):
    """Enqueue feedback event or process inline if queue unavailable."""
    q = _get_queue()
    if q is not None:
        q.enqueue(process_feedback_event, event)
        return "queued"
    # Inline fallback – mainly for local dev & tests
    process_feedback_event(event)
    return "inline"


def process_feedback_event(event: Dict[str, Any]) -> np.ndarray | None:
    """Apply feedback to a user's profile vector.

    Parameters
    ----------
    event : Dict[str, Any]
        JSON-serialisable dictionary with keys ``user_id``, ``content_id`` and ``feedback_type``.

    Returns
    -------
    np.ndarray | None
        The updated user profile vector, or *None* if an unrecoverable error occurred.
    """
    try:
        user_id: str = str(event["user_id"])
        content_id: str = str(event["content_id"])
        feedback_type = FeedbackType(event["feedback_type"])

        store = get_vector_store()
        content_vec = store.get_content_vector(content_id)

        new_vec = UserProfileVectorManager.apply_feedback(user_id, content_vec, feedback_type)
        logger.info("Processed feedback for user %s with type %s", user_id, feedback_type.value)
        return new_vec
    except Exception as exc:  # pragma: no cover – ensure worker never crashes the queue
        logger.exception("Failed to process feedback event: %s", exc)
        return None


if __name__ == "__main__":
    q = _get_queue()
    if q is None:
        print("Redis/RQ not available. Install redis & rq and ensure REDIS_URL is set.")
    else:
        print("[*] Starting feedback worker, listening on 'feedback' queue")
        Worker([q]).work() 