"""
Vector Mathematics Module for User Profile Updates
"""

import numpy as np
from enum import Enum
from typing import Dict
from src.storage.vector_store import get_vector_store
from math import isclose

class FeedbackType(Enum):
    LIKE = "LIKE"
    HIDE = "HIDE"
    NOT_RELEVANT = "NOT_RELEVANT"
    NOT_NOW = "NOT_NOW"
    TOO_SUPERFICIAL = "TOO_SUPERFICIAL"
    TOO_ADVANCED = "TOO_ADVANCED"


def update_and_normalize_vector(old_vector, content_vector, weight):
    """Update profile vector with weighted content vector and return a unit vector."""
    old_vector = np.array(old_vector, dtype=np.float32)
    content_vector = np.array(content_vector, dtype=np.float32)

    if old_vector.shape != content_vector.shape:
        raise ValueError("Vectors must have the same dimensions")

    updated_vector = old_vector + (weight * content_vector)
    norm = np.linalg.norm(updated_vector)

    if norm == 0:
        return np.zeros_like(updated_vector)

    return updated_vector / norm


# Default weights mapping (fallback)
DEFAULT_WEIGHTS: Dict[FeedbackType, float] = {
    FeedbackType.LIKE: 0.10,
    FeedbackType.HIDE: -0.15,
    FeedbackType.NOT_RELEVANT: -0.05,
    FeedbackType.NOT_NOW: -0.02,
    FeedbackType.TOO_SUPERFICIAL: -0.03,
    FeedbackType.TOO_ADVANCED: -0.04,
}


def project_vector(vector: np.ndarray, direction: np.ndarray) -> np.ndarray:
    """Project *vector* onto *direction* and return the projection component."""
    v = np.asarray(vector, dtype=float)
    d = np.asarray(direction, dtype=float)
    if v.shape != d.shape:
        raise ValueError("Vector and direction must have the same dimensions")

    denom = np.dot(d, d)
    if isclose(denom, 0.0):
        return np.zeros_like(v)

    return (np.dot(v, d) / denom) * d


class UserProfileVectorManager:
    """Manager that updates & persists user profile vectors according to feedback."""

    _store = get_vector_store()

    @classmethod
    def get_vector(cls, user_id: str, dimension: int = 1536):
        """Fetch existing vector or initialize a zero vector of the given dimension."""
        return cls._store.get_user_vector(user_id, dimension)

    @classmethod
    def apply_feedback(
        cls,
        user_id: str,
        content_vector: np.ndarray,
        feedback_type: FeedbackType,
        weight: float | None = None,
    ) -> np.ndarray:
        """Apply feedback to a user's profile vector and persist the updated vector."""
        if weight is None:
            weight = DEFAULT_WEIGHTS.get(feedback_type, 0.0)

        old_vec = cls.get_vector(user_id, dimension=len(content_vector))

        # Handle nuanced feedback types with projection logic
        if feedback_type == FeedbackType.TOO_SUPERFICIAL:
            # Reduce alignment with the content direction
            new_vec = update_and_normalize_vector(old_vec, content_vector, -abs(weight))
        elif feedback_type == FeedbackType.TOO_ADVANCED:
            # Reduce the specific component (content minus general) in the profile
            proj = project_vector(content_vector, old_vec)
            specific = content_vector - proj
            new_vec = update_and_normalize_vector(old_vec, specific, -abs(weight))
        else:
            # Standard LIKE / HIDE style updates
            new_vec = update_and_normalize_vector(old_vec, content_vector, weight)

        cls._store.save_user_vector(user_id, new_vec)
        return new_vec