import logging
from typing import Any

class ErrorHandlerNode:
    """Node responsible for converting runtime exceptions into a failed ContentState.

    This node is **not** part of the happy-path execution flow – instead, it can be
    used as an error-edge target from any LangGraph node or invoked manually by the
    orchestrator after all retry attempts have been exhausted.

    The implementation purposefully keeps external dependencies to a minimum so
    that it can be imported and used in isolation (e.g. from notebooks or ad-hoc
    scripts).
    """

    def __init__(self, retry_manager: "RetryManager | None" = None) -> None:  # type: ignore[name-defined]
        # Local import to avoid a heavy import graph for callers that only need the
        # error handler.
        from src.orchestrator.main import OrchestratorConfig, RetryManager  # pylint: disable=import-inside-function,cyclic-import

        # If no retry manager is supplied we create a default one based on the
        # global orchestrator configuration.  This keeps behaviour consistent
        # with the rest of the application while still allowing the node to be
        # configured independently for testing.
        self.retry_manager = retry_manager or RetryManager(OrchestratorConfig().retry_config)
        self._logger = logging.getLogger(__name__)

    # NOTE: `state` is intentionally typed as *Any* to avoid a hard dependency on
    # the full ContentState TypedDict at import time.  At runtime the node
    # expects a mutable mapping that supports `.copy()` – this matches both
    # TypedDicts **and** simple dicts used in tests.
    def __call__(self, state: "dict[str, Any]", error: Exception | None = None) -> "dict[str, Any]":
        """Handle an exception and return an updated *failed* state.

        Args:
            state: The current *ContentState* (or compatible dict).
            error: The exception that triggered the error edge.  If *None* the
                   node becomes a *no-op* and simply returns the state
                   unchanged.

        Returns:
            The (possibly) modified state.  If *error* is provided the returned
            state is marked as *failed* and enriched with diagnostic
            information so that downstream monitoring / dashboards can surface
            meaningful insights.
        """
        # Fast-path: nothing to do – propagating the state untouched keeps the
        # node transparent for success branches that might call it accidentally.
        if error is None:
            return state

        from datetime import datetime, timezone  # Local import saves ~7 ms on cold start
        from src.orchestrator.main import ErrorClassifier  # pylint: disable=import-inside-function,cyclic-import

        # Copy the incoming state to guarantee immutability.
        updated_state = state.copy()

        # Classify the exception to determine severity / retry logic.
        error_type = ErrorClassifier.classify_error(error)
        updated_state["status"] = "failed"
        updated_state["error_message"] = str(error)
        updated_state["error_type"] = error_type.value
        updated_state["processed_at"] = datetime.now(timezone.utc).isoformat()

        # Increment retry count if it exists; initialise otherwise.
        updated_state["retry_count"] = int(updated_state.get("retry_count", 0)) + 1

        # Log in structured form so that external observability tools like
        # LangSmith can parse it easily.
        self._logger.error(
            "ErrorHandlerNode captured error | type=%s | message=%s | retries=%s",
            error_type.value,
            error,
            updated_state["retry_count"],
        )

        # Decide whether the orchestrator *should* attempt another retry.  We do
        # **not** raise here because retry orchestration is handled at a higher
        # level (see Orchestrator._process_content_with_retry).  Instead we
        # attach a hint that upstream logic can inspect.
        updated_state["should_retry"] = self.retry_manager.should_retry(
            error, updated_state["retry_count"] - 1
        )

        return updated_state
