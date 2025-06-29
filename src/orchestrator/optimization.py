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
from typing import Dict, List, Optional, Any, Callable, Tuple
import logging

from .state import ContentState, update_state_status
from .monitoring import get_monitor

logger = logging.getLogger(__name__)


class ContentCache:
    """Intelligent caching system for expensive operations."""
    
    def __init__(self, cache_dir: str = ".cache", max_age_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_age = timedelta(hours=max_age_hours)
        
    def _get_cache_key(self, content_type: str, url: str, params: Dict = None) -> str:
        """Generate cache key for content."""
        data = {"type": content_type, "url": url, "params": params or {}}
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    def get(self, content_type: str, url: str, params: Dict = None) -> Optional[Any]:
        """Retrieve cached content if available and fresh."""
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
            return cached_data['content']
            
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            return None
    
    def set(self, content_type: str, url: str, content: Any, params: Dict = None):
        """Store content in cache."""
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


class SmartRetryManager:
    """Intelligent retry logic with exponential backoff and error-specific strategies."""
    
    def __init__(self):
        self.retry_strategies = {
            "rate_limit": {"max_retries": 5, "base_delay": 60, "backoff": 2.0},
            "network": {"max_retries": 3, "base_delay": 5, "backoff": 2.0},
            "api_error": {"max_retries": 2, "base_delay": 10, "backoff": 1.5},
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
        """Execute function with intelligent retry logic."""
        last_error = None
        
        for attempt in range(max(s["max_retries"] for s in self.retry_strategies.values()) + 1):
            try:
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
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


class ParallelProcessor:
    """Orchestrate parallel execution of independent nodes."""
    
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