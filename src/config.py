import os
from dataclasses import dataclass

TRANSCRIPTION_METHOD = os.getenv("TRANSCRIPTION_METHOD", "local")
AUDIO_SPEED_FACTOR = float(os.getenv("AUDIO_SPEED_FACTOR", 2.0))

# -------------------------------------------------------------
# InsightHub Optimization & Caching Configuration (Task 38.5)
# -------------------------------------------------------------

# Enable or disable the new optimized execution path for the
# orchestrator. When set to ``true`` (case-insensitive) the
# orchestrator will route content through the Optimizer pipeline
# defined in ``src.orchestrator.optimization``.

ENABLE_OPTIMIZATIONS: bool = os.getenv("ENABLE_OPTIMIZATIONS", "false").lower() == "true"

# Intelligent cache tuning parameters. These values are consumed by
# ``ContentCache`` (see ``src/orchestrator/optimization.py``).

# Maximum age (in hours) after which a cached entry becomes stale and
# is evicted automatically on next access. Defaults to 24 h.
IH_CACHE_MAX_AGE_HOURS: int = int(os.getenv("IH_CACHE_MAX_AGE_HOURS", 24))

# Maximum number of cached items kept on disk. When the limit is
# exceeded, the oldest entries are pruned (LRU strategy).
IH_CACHE_MAX_ITEMS: int = int(os.getenv("IH_CACHE_MAX_ITEMS", 1000))

# Minutes between automatic metrics-driven tuning cycles. Default 30.
METRICS_TUNE_INTERVAL_MIN: int = int(os.getenv("METRICS_TUNE_INTERVAL_MIN", 30))

# Maximum seconds a single retry attempt can run before being considered a
# TTFB timeout. Used by SmartRetryManager to abort hung operations early.
RETRY_TIMEOUT_SEC: int = int(os.getenv("RETRY_TIMEOUT_SEC", 30))

# ---------------------------------------------------------------------------
# Centralized settings objects (addresses CODE_QUALITY audit recommendation)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class OptimizationSettings:
    """Immutable view of optimization-related configuration.

    Prefer importing this dataclass over direct constant access in new code to
    promote consistent configuration handling across the codebase.
    """

    enable_optimizations: bool = ENABLE_OPTIMIZATIONS
    cache_max_age_hours: int = IH_CACHE_MAX_AGE_HOURS
    cache_max_items: int = IH_CACHE_MAX_ITEMS
    metrics_tune_interval_min: int = METRICS_TUNE_INTERVAL_MIN


# Convenience singleton instance
OPTIMIZATION_SETTINGS = OptimizationSettings()
