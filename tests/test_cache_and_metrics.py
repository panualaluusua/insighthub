"""Unit tests for optimization components (Task 38.5).

These tests cover:
1. `ContentCache` basic store / retrieve and LRU eviction behaviour.
2. `aggregate_workflow_metrics` helper aggregation logic.
"""

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone

import pytest

# Import target modules
from src.orchestrator.optimization import ContentCache
from src.orchestrator.monitoring.metrics import (
    NodeMetrics,
    WorkflowMetrics,
    aggregate_workflow_metrics,
)


# ---------------------------------------------------------------------------
# ContentCache tests
# ---------------------------------------------------------------------------


def test_content_cache_store_and_retrieve():
    """Verify that items can be stored and retrieved successfully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = ContentCache(cache_dir=tmpdir, max_age_hours=1, max_items=10)

        key_url = "https://example.com/article"
        payload = {"foo": "bar"}
        cache.set("article", key_url, payload)

        retrieved = cache.get("article", key_url)
        assert retrieved == payload, "Cached payload should be retrievable intact"


def test_content_cache_lru_eviction():
    """Ensure that the LRU eviction removes oldest files beyond max_items."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = ContentCache(cache_dir=tmpdir, max_age_hours=1, max_items=2)

        # Insert three distinct items
        cache.set("type1", "url1", {"v": 1})
        cache.set("type1", "url2", {"v": 2})
        cache.set("type1", "url3", {"v": 3})  # Should trigger eviction

        files = [p for p in os.listdir(tmpdir) if p.endswith(".json")]
        assert len(files) == 2, "Cache should keep only `max_items` newest files"

        # The remaining files correspond to the most recent URLs (url2 and url3)
        # Verify that url1 is evicted
        assert cache.get("type1", "url1") is None


# ---------------------------------------------------------------------------
# Metrics aggregation tests
# ---------------------------------------------------------------------------


def _create_wf(node_durations):
    """Helper to build WorkflowMetrics from a mapping node_name->duration"""
    wf = WorkflowMetrics(
        workflow_id="wf1",
        start_time=datetime.now(),  # naive datetime to match NodeMetrics.complete()
        content_type="test",
    )
    for name, dur in node_durations.items():
        nm = NodeMetrics(
            node_name=name,
            execution_id=f"{name}-1",
            start_time=datetime.now() - timedelta(seconds=dur),
        )
        nm.complete()
        nm.duration = dur  # Override with supplied duration
        wf.add_node(nm)
    wf.complete()
    return wf


def test_aggregate_workflow_metrics():
    """Validate p95, avg duration and error rate calculations."""
    wf1 = _create_wf({"summarizer": 5, "embedding": 2})
    wf2 = _create_wf({"summarizer": 7, "embedding": 3})
    wf3 = _create_wf({"summarizer": 20, "embedding": 4})

    metrics = aggregate_workflow_metrics([wf1, wf2, wf3])

    # Durations for summarizer: [5,7,20] → p95 ~ 20, avg ~ 10.67
    summarizer_stats = metrics["summarizer"]
    assert summarizer_stats["count"] == 3
    assert summarizer_stats["p95_duration"] >= 20 - 1  # allow minor rounding
    assert 9 < summarizer_stats["avg_duration"] < 12

    # Embedding durations: [2,3,4]
    embedding_stats = metrics["embedding"]
    assert embedding_stats["count"] == 3
    assert embedding_stats["error_rate"] == 0.0
    assert embedding_stats["p95_duration"] >= 4 - 0.5 