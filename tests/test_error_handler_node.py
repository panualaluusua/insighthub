import pytest
from datetime import datetime, timezone

from src.orchestrator.nodes.error_handler import ErrorHandlerNode


@pytest.fixture()
def base_state():
    """Return a minimal ContentState-like dict for testing."""
    return {
        "source_url": "https://example.com",
        "status": "pending",
    }


def test_no_error_returns_state_unchanged(base_state):
    node = ErrorHandlerNode()
    result = node(base_state)
    # Should be exactly the same object (identity preserved) and unchanged
    assert result is base_state


def test_network_error_enrichment_and_retry(base_state):
    node = ErrorHandlerNode()
    err = ConnectionError("Network unreachable")
    result = node(base_state, err)
    assert result["status"] == "failed"
    assert result["error_type"] == "network"
    assert result["should_retry"] is True
    assert isinstance(result["retry_count"], int) and result["retry_count"] == 1
    # processed_at should be recent iso timestamp
    processed_time = datetime.fromisoformat(result["processed_at"])
    assert processed_time.tzinfo is not None  # timezone aware


def test_permanent_error_no_retry(base_state):
    node = ErrorHandlerNode()
    err = PermissionError("403 Forbidden")
    result = node(base_state, err)
    assert result["status"] == "failed"
    assert result["error_type"] == "permanent"
    assert result["should_retry"] is False 