"""Optimization metrics tuner (Task 38.5).

Periodically aggregates recent workflow metrics from the local monitor
and tunes AdaptiveModelSelector & SmartRetryManager instances.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, TYPE_CHECKING

from src import config as app_config

# Runtime imports
from src.orchestrator.monitoring import WorkflowMetrics, get_monitor
from src.orchestrator.monitoring.metrics import aggregate_workflow_metrics

# Avoid circular import by only importing types during type checking
if TYPE_CHECKING:  # pragma: no cover
    from src.orchestrator.optimization import AdaptiveModelSelector, SmartRetryManager

logger = logging.getLogger(__name__)


class OptimizerMetricsTuner:
    """Collect metrics and tune optimization components at fixed intervals."""

    def __init__(
        self,
        selector: "AdaptiveModelSelector",
        retry_manager: "SmartRetryManager",
        interval_minutes: int = app_config.OPTIMIZATION_SETTINGS.metrics_tune_interval_min,
    ) -> None:
        self.selector = selector
        self.retry_manager = retry_manager
        self.interval = timedelta(minutes=interval_minutes)
        self._last_run: Optional[datetime] = None

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    def maybe_run(self) -> None:
        """Run tuning if the interval has elapsed."""
        now = datetime.now()
        if self._last_run and now - self._last_run < self.interval:
            return  # Not yet time

        try:
            monitor = get_monitor()
            workflows: List[WorkflowMetrics] = list(monitor.recent_workflows)
            if not workflows:
                return

            node_stats = aggregate_workflow_metrics(workflows)
            self.selector.update_from_metrics(node_stats)

            # Build simple error stats mapping using node_stats
            error_stats: Dict[str, int] = {
                n: stats["error_count"] for n, stats in node_stats.items()
            }
            self.retry_manager.tune_from_metrics(error_stats)

            self._last_run = now
            logger.info("Metrics tuner updated optimization strategies (interval %s min)", self.interval.total_seconds()/60)
        except Exception as e:
            logger.warning("Metrics tuner failed: %s", e) 