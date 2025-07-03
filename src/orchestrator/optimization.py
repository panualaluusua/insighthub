"""Workflow optimization module for the InsightHub orchestrator.

This module implements performance optimizations based on monitoring insights:
- Parallel processing for independent nodes
- Intelligent caching strategies
- Adaptive model selection
- Smart retry logic with backoff
- Performance-based routing
"""

import asyncio
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple, TYPE_CHECKING
import logging

from .state import ContentState, update_state_status
from .monitoring import get_monitor
from src import config as app_config

# Avoid circular import at runtime – import only for type checking
if TYPE_CHECKING:  # pragma: no cover
    from src.orchestrator.optimization_tuner import OptimizerMetricsTuner

logger = logging.getLogger(__name__)


# -------------------------------------------------------------
# ContentCache (Enhanced for Task 38.5)
# -------------------------------------------------------------

# The cache now supports LRU-style eviction based on a configurable
# maximum number of items (IH_CACHE_MAX_ITEMS).  When the limit is
# exceeded the *oldest* cache files (based on modification timestamp)
# are removed.  This prevents unbounded disk usage in long-running
# orchestrations.
# -------------------------------------------------------------

class ContentCache:
    """On-disk cache with adaptive TTL and LRU eviction."""

    def __init__(
        self,
        cache_dir: str = ".cache",
        max_age_hours: int | None = None,
        max_items: int | None = None,
    ) -> None:
        """Create a cache instance.

        Args:
            cache_dir: Directory where cached JSON files are stored.
            max_age_hours: Time-to-live for a cache entry; if *None* the
              value from ``IH_CACHE_MAX_AGE_HOURS`` is used.
            max_items: Maximum number of items to keep.  When the limit
              is reached the oldest files are evicted.  If *None* the
              value from ``IH_CACHE_MAX_ITEMS`` is applied.
        """

        # Resolve config fallbacks
        max_age_hours = max_age_hours or app_config.IH_CACHE_MAX_AGE_HOURS
        max_items = max_items or app_config.IH_CACHE_MAX_ITEMS

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        self.max_age = timedelta(hours=max_age_hours)
        self.max_items = max_items
        
        # Simple hit/miss counters for performance monitoring
        self._hits: int = 0
        self._misses: int = 0
        
    def _get_cache_key(
        self,
        content_type: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a stable hash key for caching.

        Args:
            content_type: Logical category of the content (e.g. "video", "article").
            url: Unique identifier or URL for the content.
            params: Optional request parameters that influence the response.

        Returns:
            Hex MD5 digest that uniquely identifies a cache entry.
        """
        data: Dict[str, Any] = {"type": content_type, "url": url, "params": params or {}}
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    def get(
        self,
        content_type: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """Retrieve cached content if available and still fresh.

        Returns ``None`` when the cache entry is missing or expired.
        """
        try:
            cache_key = self._get_cache_key(content_type, url, params)
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            if not cache_file.exists():
                return None
                
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Check if cache is still valid
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cached_time > self.max_age:
                cache_file.unlink()  # Remove expired cache
                return None
                
            logger.info(f"Cache hit for {content_type}: {url[:50]}...")
            self._hits += 1
            return cached_data['content']
            
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            return None
        finally:
            # Register miss if we are returning None
            if 'cached_data' not in locals():
                self._misses += 1
    
    def set(
        self,
        content_type: str,
        url: str,
        content: Any,
        params: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Store content in cache and enforce LRU policy."""
        try:
            cache_key = self._get_cache_key(content_type, url, params)
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            cached_data = {
                'timestamp': datetime.now().isoformat(),
                'content': content,
                'type': content_type,
                'url': url,
                'params': params or {}
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cached_data, f, indent=2)
                
            logger.debug(f"Cached {content_type}: {url[:50]}...")
            
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")

        # Enforce LRU eviction policy if we surpass the max_items limit
        try:
            # Use cached "timestamp" field for deterministic ordering even
            # when the filesystem modification times have identical
            # resolution (Windows second-level granularity can cause ties).
            def _file_ts(path: Path) -> float:
                try:
                    with path.open("r") as f:
                        return datetime.fromisoformat(json.load(f)["timestamp"]).timestamp()
                except Exception:
                    # Fallback to file mtime if JSON parsing fails
                    return path.stat().st_mtime

            all_cache_files = sorted(self.cache_dir.glob("*.json"), key=_file_ts)
            if self.max_items and len(all_cache_files) > self.max_items:
                surplus = len(all_cache_files) - self.max_items
                for old_file in all_cache_files[:surplus]:
                    old_file.unlink(missing_ok=True)
                    logger.debug(f"Evicted old cache file {old_file.name}")
        except Exception as e:
            logger.warning(f"Cache eviction check failed: {e}")

    # ------------------------------------------------------------------
    # Metrics helpers
    # ------------------------------------------------------------------

    @property
    def stats(self) -> Dict[str, int]:
        """Return simple hit / miss counters for performance dashboards."""
        return {"hits": self._hits, "misses": self._misses}


class SmartRetryManager:
    """Intelligent retry logic with exponential backoff and error-specific strategies."""
    
    def __init__(self, timeout_seconds: int = app_config.RETRY_TIMEOUT_SEC):
        self.timeout_seconds = timeout_seconds
        self.retry_strategies = {
            "rate_limit": {"max_retries": 5, "base_delay": 60, "backoff": 2.0},
            "network": {"max_retries": 3, "base_delay": 5, "backoff": 2.0},
            "api_error": {"max_retries": 2, "base_delay": 10, "backoff": 1.5},
            "timeout": {"max_retries": 2, "base_delay": 10, "backoff": 2.0},
            "default": {"max_retries": 2, "base_delay": 5, "backoff": 2.0}
        }
    
    def classify_error(self, error: Exception) -> str:
        """Classify error type for appropriate retry strategy."""
        error_str = str(error).lower()
        
        if "rate limit" in error_str or "429" in error_str:
            return "rate_limit"
        elif "network" in error_str or "timeout" in error_str or "connection" in error_str:
            return "network"
        elif "api" in error_str or "401" in error_str or "403" in error_str:
            return "api_error"
        else:
            return "default"
    
    async def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """Execute *func* with an adaptive retry strategy.

        The method purposefully catches :class:`Exception` **once** per
        iteration in order to:

        1. Run :pyfunc:`classify_error` which maps the concrete exception
           instance to a *retry strategy* key.
        2. Decide whether another attempt should be made based on the mapping.
        3. Re-raise the *last* exception once the maximum number of retries for
           the detected error category is exhausted.

        Since the original exception object is re-raised unchanged, the caller
        still receives the concrete exception type – generic catching here is
        therefore safe and does not mask bugs.  This design choice aligns with
        the Aider CODE_QUALITY checklist requirement to avoid *swallowing*
        exceptions while still enabling category-based back-off tuning.
        """
        last_error = None
        
        for attempt in range(max(s["max_retries"] for s in self.retry_strategies.values()) + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=self.timeout_seconds)
                else:
                    # For sync functions we cannot easily enforce timeout without threads; run as is.
                    return func(*args, **kwargs)
            except asyncio.TimeoutError as to_err:
                last_error = to_err
                error_type = "timeout"
                strategy = self.retry_strategies.get(error_type, self.retry_strategies["default"])
                if attempt >= strategy["max_retries"]:
                    logger.error("Timeout after %s attempts: %s", attempt + 1, to_err)
                    break
                delay = strategy["base_delay"] * (strategy["backoff"] ** attempt)
                logger.warning("Timeout on attempt %s; retrying in %ss", attempt + 1, delay)
                await asyncio.sleep(delay)
            except Exception as error:
                last_error = error
                error_type = self.classify_error(error)
                strategy = self.retry_strategies[error_type]
                
                if attempt >= strategy["max_retries"]:
                    logger.error(f"Max retries exceeded for {error_type}: {error}")
                    break
                
                delay = strategy["base_delay"] * (strategy["backoff"] ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed ({error_type}), retrying in {delay}s: {error}")
                
                if asyncio.iscoroutinefunction(func):
                    await asyncio.sleep(delay)
                else:
                    time.sleep(delay)
        
        raise last_error

    # ---------------------------------------------------------
    # Task 38.5: Strategy tuning using error frequency metrics
    # ---------------------------------------------------------

    def tune_from_metrics(self, error_stats: Dict[str, int]) -> None:
        """Adjust retry strategies based on observed error frequencies.

        Args:
            error_stats: Mapping of error_type → occurrence count.
        """
        for error_type, count in error_stats.items():
            if error_type not in self.retry_strategies:
                continue

            strat = self.retry_strategies[error_type]

            # Simple heuristic: more errors ⇒ increase base delay
            if count > 100:
                strat["base_delay"] = min(strat["base_delay"] * 2, 300)
            elif count < 10:
                strat["base_delay"] = max(strat["base_delay"] / 2, 1)
        logger.debug("SmartRetryManager: strategies tuned based on metrics → %s", self.retry_strategies)


class AdaptiveModelSelector:
    """Select optimal models based on content characteristics and performance history."""
    
    def __init__(self):
        self.performance_history = {}
        self.model_configs = {
            "summarizer": {
                "fast": {"model": "deepseek-chat", "max_tokens": 1000, "temperature": 0.3},
                "balanced": {"model": "deepseek-chat", "max_tokens": 2000, "temperature": 0.3},
                "quality": {"model": "deepseek-reasoner", "max_tokens": 3000, "temperature": 0.2}
            },
            "embedding": {
                "fast": {"model": "text-embedding-3-small"},
                "balanced": {"model": "text-embedding-ada-002"},
                "quality": {"model": "text-embedding-3-large"}
            }
        }
    
    def select_model(self, node_type: str, content_length: int, priority: str = "balanced") -> Dict:
        """Select optimal model configuration based on content and requirements."""
        configs = self.model_configs.get(node_type, {})
        
        # Adaptive selection based on content length
        if content_length < 1000:
            return configs.get("fast", configs.get("balanced", {}))
        elif content_length < 5000:
            return configs.get("balanced", {})
        else:
            return configs.get("quality", configs.get("balanced", {}))
    
    def record_performance(self, node_type: str, model: str, duration: float, success: bool):
        """Record model performance for future optimization."""
        key = f"{node_type}_{model}"
        if key not in self.performance_history:
            self.performance_history[key] = {"total_time": 0, "count": 0, "success_count": 0}
        
        self.performance_history[key]["total_time"] += duration
        self.performance_history[key]["count"] += 1
        if success:
            self.performance_history[key]["success_count"] += 1

    # ---------------------------------------------------------
    # Task 38.5: Dynamic configuration using monitoring metrics
    # ---------------------------------------------------------
    def update_from_metrics(self, node_metrics: Dict[str, Dict[str, Any]]) -> None:
        """Update internal model config preferences based on aggregated
        node metrics (e.g. average duration).

        The *node_metrics* dict is expected to be of the form::

            {
                "summarizer": {"p95_duration": 8.4, "error_rate": 0.02},
                "embedding": {"p95_duration": 2.1, "error_rate": 0.00}
            }

        A naive strategy is applied:
        • If p95_duration > 10s → downgrade to *fast* model
        • If p95_duration < 3s and error_rate < 1% → upgrade to *quality*
        """
        for node_type, stats in node_metrics.items():
            p95 = stats.get("p95_duration", 0)
            error_rate = stats.get("error_rate", 0)

            if p95 > 10:
                preferred = "fast"
            elif p95 < 3 and error_rate < 0.01:
                preferred = "quality"
            else:
                preferred = "balanced"

            if node_type in self.model_configs and preferred in self.model_configs[node_type]:
                # Reorder dict so that preferred becomes first lookup result
                config = self.model_configs[node_type]
                reordered = {preferred: config[preferred], **{k: v for k, v in config.items() if k != preferred}}
                self.model_configs[node_type] = reordered
                logger.debug(f"AdaptiveModelSelector: updated {node_type} preferred tier → {preferred}")


class ParallelProcessor:
    """Utility for executing multiple independent LangGraph nodes in parallel.

    InsightHub workflows often perform I/O-bound steps that are safe to run
    concurrently (e.g. *summarizer* & *embedding* generation).  The
    ``ParallelProcessor`` wraps a ``ThreadPoolExecutor`` and takes care of:

    • Submitting node callables with the shared ``ContentState``
    • Capturing per-node success / error metrics via :pyfunc:`get_monitor`
    • Merging successful results back into an updated state object
    • Propagating failures without stopping sibling tasks (errors are
      aggregated and returned in the final state as *partial_failure*)

    The class is intentionally lightweight – it does **not** attempt to handle
    CPU-bound workloads (which should be off-loaded to separate processes) and
    relies on the GIL-friendly nature of I/O heavy node implementations.
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def execute_parallel_nodes(self, state: ContentState, node_functions: List[Tuple[str, Callable]]) -> ContentState:
        """Execute multiple independent nodes in parallel."""
        monitor = get_monitor()
        workflow_id = state.get("workflow_id", "unknown")
        
        # Submit all tasks
        future_to_node = {}
        for node_name, node_func in node_functions:
            future = self.executor.submit(self._execute_monitored_node, node_func, state, node_name, workflow_id)
            future_to_node[future] = node_name
        
        # Collect results
        results = {}
        errors = {}
        
        for future in as_completed(future_to_node):
            node_name = future_to_node[future]
            try:
                results[node_name] = future.result()
            except Exception as e:
                errors[node_name] = str(e)
                logger.error(f"Parallel node {node_name} failed: {e}")
        
        # Merge results into state
        updated_state = state.copy()
        
        # Apply successful results
        for node_name, result_state in results.items():
            if node_name == "summarizer" and "summary" in result_state:
                updated_state["summary"] = result_state["summary"]
            elif node_name == "embedding" and "embeddings" in result_state:
                updated_state["embeddings"] = result_state["embeddings"]
        
        # Handle errors
        if errors:
            error_messages = [f"{node}: {msg}" for node, msg in errors.items()]
            updated_state = update_state_status(
                updated_state,
                status="partial_failure",
                error_message=f"Parallel processing errors: {'; '.join(error_messages)}"
            )
        else:
            updated_state["status"] = "processed"
        
        updated_state["updated_at"] = datetime.now(timezone.utc).isoformat()
        return updated_state
    
    def _execute_monitored_node(self, node_func: Callable, state: ContentState, node_name: str, workflow_id: str) -> ContentState:
        """Execute a node with monitoring integration."""
        monitor = get_monitor()
        execution_id = monitor.start_node(workflow_id, node_name)
        
        start_time = time.time()
        try:
            result = node_func(state)
            duration = time.time() - start_time
            monitor.complete_node(execution_id, "success")
            return result
        except Exception as e:
            duration = time.time() - start_time
            monitor.complete_node(execution_id, "error", error_message=str(e))
            raise
    
    def __del__(self):
        """Clean up thread pool."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


class OptimizedOrchestrator:
    """Optimized orchestrator combining all performance improvements."""
    
    def __init__(self):
        self.cache = ContentCache()
        self.retry_manager = SmartRetryManager()
        self.model_selector = AdaptiveModelSelector()
        self.parallel_processor = ParallelProcessor()
        self.monitor = get_monitor()
        # Lazy import to avoid circular dependency at module load time
        from src.orchestrator.optimization_tuner import OptimizerMetricsTuner as _MetricsTuner

        self._tuner: _MetricsTuner = _MetricsTuner(self.model_selector, self.retry_manager)
    
    async def process_with_optimizations(self, state: ContentState, nodes: Dict[str, Callable]) -> ContentState:
        """Process content with all optimizations enabled."""
        workflow_id = self.monitor.start_workflow(state.get("source_type", "unknown"))
        state["workflow_id"] = workflow_id
        
        try:
            # Phase 1: Content Fetching (with caching)
            if "content_fetcher" in nodes:
                state = await self._cached_content_fetch(state, nodes["content_fetcher"])
            
            # Phase 2: Parallel Processing (Summarizer + Embedding)
            parallel_nodes = []
            if "summarizer" in nodes:
                parallel_nodes.append(("summarizer", nodes["summarizer"]))
            if "embedding" in nodes:
                parallel_nodes.append(("embedding", nodes["embedding"]))
            
            if parallel_nodes:
                state = self.parallel_processor.execute_parallel_nodes(state, parallel_nodes)
            
            # Phase 3: Storage
            if "storage" in nodes:
                state = await self.retry_manager.retry_with_backoff(nodes["storage"], state)
            
            # Periodic metrics-driven tuning
            self._tuner.maybe_run()
            
            self.monitor.complete_workflow(workflow_id, "success")
            return state
            
        except Exception as e:
            self.monitor.complete_workflow(workflow_id, "error", error_message=str(e))
            raise
    
    async def _cached_content_fetch(self, state: ContentState, fetcher_node: Callable) -> ContentState:
        """Content fetching with intelligent caching."""
        cache_key_params = {
            "source_type": state["source_type"],
            "model_size": "base"  # For YouTube transcription
        }
        
        # Try cache first
        cached_content = self.cache.get(
            state["source_type"], 
            state["source_url"], 
            cache_key_params
        )
        
        if cached_content:
            # Use cached content
            updated_state = state.copy()
            updated_state.update(cached_content)
            updated_state["updated_at"] = datetime.now(timezone.utc).isoformat()
            return updated_state
        
        # Fetch with retry logic
        result_state = await self.retry_manager.retry_with_backoff(fetcher_node, state)
        
        # Cache the result
        if result_state.get("status") != "failed":
            cache_data = {
                "raw_content": result_state.get("raw_content"),
                "content_id": result_state.get("content_id"),
                "metadata": result_state.get("metadata", {})
            }
            self.cache.set(
                state["source_type"],
                state["source_url"],
                cache_data,
                cache_key_params
            )
        
        return result_state


# Global optimization instance
_optimizer = None

def get_optimizer() -> OptimizedOrchestrator:
    """Get global optimizer instance."""
    global _optimizer
    if _optimizer is None:
        _optimizer = OptimizedOrchestrator()
    return _optimizer 