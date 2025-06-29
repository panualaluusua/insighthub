"""Main Orchestrator class for InsightHub content processing."""

import logging
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Callable, Any, Dict
from threading import Lock
from enum import Enum

from src.orchestrator.graph import create_orchestrator_graph
from src.orchestrator.state import ContentState, create_content_state

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Classification of error types for different handling strategies."""
    TRANSIENT = "transient"  # Temporary errors that can be retried
    PERMANENT = "permanent"  # Permanent errors that should not be retried
    RATE_LIMITED = "rate_limited"  # Rate limiting errors
    NETWORK = "network"  # Network connectivity issues
    TIMEOUT = "timeout"  # Timeout errors
    UNKNOWN = "unknown"  # Unclassified errors


class RetryStrategy(Enum):
    """Retry strategies for different error types."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    FIXED_DELAY = "fixed_delay"
    LINEAR_BACKOFF = "linear_backoff"


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    jitter_enabled: bool = True
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_max_calls: int = 3


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, requests are rejected
    HALF_OPEN = "half_open"  # Testing if service has recovered


@dataclass
class CircuitBreaker:
    """Circuit breaker implementation for preventing cascading failures."""
    
    service_name: str
    config: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    half_open_calls: int = 0
    _lock: Lock = field(default_factory=Lock)
    
    def can_execute(self) -> bool:
        """Check if execution is allowed based on circuit breaker state."""
        with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                # Check if we should transition to half-open
                if (self.last_failure_time and 
                    (datetime.now(timezone.utc) - self.last_failure_time).total_seconds() >= self.config.recovery_timeout):
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.half_open_calls = 0
                    logger.info(f"Circuit breaker for {self.service_name} transitioning to HALF_OPEN")
                    return True
                return False
            else:  # HALF_OPEN
                return self.half_open_calls < self.config.half_open_max_calls
    
    def record_success(self) -> None:
        """Record a successful operation."""
        with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.half_open_calls += 1
                if self.half_open_calls >= self.config.half_open_max_calls:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    logger.info(f"Circuit breaker for {self.service_name} transitioning to CLOSED")
            elif self.state == CircuitBreakerState.CLOSED:
                self.failure_count = 0
    
    def record_failure(self) -> None:
        """Record a failed operation."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now(timezone.utc)
            
            if self.state in [CircuitBreakerState.CLOSED, CircuitBreakerState.HALF_OPEN]:
                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitBreakerState.OPEN
                    logger.warning(f"Circuit breaker for {self.service_name} transitioning to OPEN after {self.failure_count} failures")


@dataclass
class OrchestratorConfig:
    """Configuration for the Orchestrator."""
    
    max_concurrent_jobs: int = 5
    timeout_seconds: int = 300
    max_retries: int = 3
    enable_progress_tracking: bool = True
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    circuit_breaker_config: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    enable_circuit_breaker: bool = True
    
    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.max_concurrent_jobs <= 0:
            raise ValueError("max_concurrent_jobs must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")


@dataclass
class ProcessingProgress:
    """Progress tracking for batch processing operations."""
    
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    retried_items: int = 0
    circuit_breaker_rejected: int = 0
    current_status: str = "idle"
    start_time: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100.0
    
    @property
    def is_complete(self) -> bool:
        """Check if processing is complete."""
        return self.completed_items + self.failed_items >= self.total_items
    
    def update_status(self, status: str) -> None:
        """Update the current status."""
        self.current_status = status
        logger.info(f"Processing status: {status}")


class ErrorClassifier:
    """Classifies errors into different types for appropriate handling."""
    
    @staticmethod
    def classify_error(error: Exception) -> ErrorType:
        """
        Classify an error into an ErrorType for appropriate handling.
        
        Args:
            error: The exception to classify.
            
        Returns:
            The classified error type.
        """
        error_message = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Network-related errors
        if any(keyword in error_message for keyword in ["connection", "network", "dns", "socket"]):
            return ErrorType.NETWORK
        
        # Timeout errors
        if any(keyword in error_message for keyword in ["timeout", "timed out"]):
            return ErrorType.TIMEOUT
        
        # Rate limiting
        if any(keyword in error_message for keyword in ["rate limit", "too many requests", "429"]):
            return ErrorType.RATE_LIMITED
        
        # Permanent errors (authentication, authorization, not found, etc.)
        if any(keyword in error_message for keyword in ["401", "403", "404", "unauthorized", "forbidden", "not found"]):
            return ErrorType.PERMANENT
        
        # Server errors that might be transient
        if any(keyword in error_message for keyword in ["500", "502", "503", "504", "server error"]):
            return ErrorType.TRANSIENT
        
        # Default to unknown for unclassified errors
        return ErrorType.UNKNOWN


class RetryManager:
    """Manages retry logic with various backoff strategies."""
    
    def __init__(self, config: RetryConfig):
        """Initialize RetryManager with configuration."""
        self.config = config
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """
        Determine if an error should be retried.
        
        Args:
            error: The exception that occurred.
            attempt: The current attempt number (0-based).
            
        Returns:
            True if the error should be retried, False otherwise.
        """
        if attempt >= self.config.max_retries:
            return False
        
        error_type = ErrorClassifier.classify_error(error)
        
        # Don't retry permanent errors
        if error_type == ErrorType.PERMANENT:
            return False
        
        # Retry transient, network, timeout, and rate-limited errors
        return error_type in [ErrorType.TRANSIENT, ErrorType.NETWORK, ErrorType.TIMEOUT, ErrorType.RATE_LIMITED, ErrorType.UNKNOWN]
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay before retry based on strategy.
        
        Args:
            attempt: The current attempt number (0-based).
            
        Returns:
            Delay in seconds before retry.
        """
        if self.config.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.config.base_delay
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * (attempt + 1)
        else:  # EXPONENTIAL_BACKOFF
            delay = self.config.base_delay * (self.config.backoff_multiplier ** attempt)
        
        # Apply maximum delay limit
        delay = min(delay, self.config.max_delay)
        
        # Add jitter if enabled
        if self.config.jitter_enabled:
            jitter = random.uniform(0.1, 0.3) * delay
            delay += jitter
        
        return delay


class Orchestrator:
    """
    Main orchestrator for content processing using LangGraph.
    
    Provides batch processing capabilities, progress tracking, error handling,
    retry logic, and circuit breaker patterns for robust content processing.
    """
    
    def __init__(self, config: Optional[OrchestratorConfig] = None) -> None:
        """
        Initialize the Orchestrator.
        
        Args:
            config: Configuration for the orchestrator. Uses defaults if None.
        """
        self.config = config or OrchestratorConfig()
        self.graph = create_orchestrator_graph()
        self._stop_requested = False
        self._current_progress = ProcessingProgress()
        self._progress_lock = Lock()
        self.retry_manager = RetryManager(self.config.retry_config)
        
        # Initialize circuit breakers for different services
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        if self.config.enable_circuit_breaker:
            self.circuit_breakers["graph_processing"] = CircuitBreaker(
                "graph_processing", 
                self.config.circuit_breaker_config
            )
        
        logger.info(f"Orchestrator initialized with config: {self.config}")
    
    def _get_circuit_breaker(self, service_name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker for a service."""
        return self.circuit_breakers.get(service_name)
    
    def process_content(self, content_state: ContentState) -> ContentState:
        """
        Process a single content item through the orchestrator graph with error handling.
        
        Args:
            content_state: The content state to process.
            
        Returns:
            The processed content state with updated status and data.
        """
        return self._process_content_with_retry(content_state)
    
    def _process_content_with_retry(self, content_state: ContentState) -> ContentState:
        """
        Process content with retry logic and circuit breaker protection.
        
        Args:
            content_state: The content state to process.
            
        Returns:
            The processed content state.
        """
        circuit_breaker = self._get_circuit_breaker("graph_processing")
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                # Check circuit breaker
                if circuit_breaker and not circuit_breaker.can_execute():
                    logger.warning("Circuit breaker is open, rejecting request")
                    # Update progress for circuit breaker rejection
                    with self._progress_lock:
                        self._current_progress.circuit_breaker_rejected += 1
                    
                    failed_state = content_state.copy()
                    failed_state["status"] = "failed"
                    failed_state["error_message"] = "Circuit breaker is open"
                    failed_state["error_type"] = "circuit_breaker"
                    failed_state["processed_at"] = datetime.now(timezone.utc).isoformat()
                    return failed_state
                
                logger.info(f"Processing content (attempt {attempt + 1}): {content_state.get('source_url', 'unknown')}")
                result = self.graph.invoke(content_state)
                
                # Record success with circuit breaker
                if circuit_breaker:
                    circuit_breaker.record_success()
                
                logger.info(f"Content processing completed successfully")
                return result
                
            except Exception as e:
                last_error = e
                error_type = ErrorClassifier.classify_error(e)
                
                logger.error(f"Error processing content (attempt {attempt + 1}): {e}")
                logger.debug(f"Error classified as: {error_type.value}")
                
                # Record failure with circuit breaker
                if circuit_breaker:
                    circuit_breaker.record_failure()
                
                # Check if we should retry
                if not self.retry_manager.should_retry(e, attempt):
                    logger.info(f"Not retrying error: {error_type.value}")
                    break
                
                # Don't retry on last attempt
                if attempt >= self.config.max_retries:
                    break
                
                # Calculate and apply delay
                delay = self.retry_manager.calculate_delay(attempt)
                logger.info(f"Retrying in {delay:.2f} seconds...")
                
                # Update progress for retry
                with self._progress_lock:
                    self._current_progress.retried_items += 1
                
                time.sleep(delay)
        
        # All retries exhausted, create failed state
        failed_state = content_state.copy()
        failed_state["status"] = "failed"
        failed_state["error_message"] = str(last_error) if last_error else "Unknown error"
        failed_state["error_type"] = ErrorClassifier.classify_error(last_error).value if last_error else "unknown"
        failed_state["retry_count"] = self.config.retry_config.max_retries
        failed_state["processed_at"] = datetime.now(timezone.utc).isoformat()
        
        return failed_state
    
    def process_batch(
        self, 
        content_list: List[ContentState],
        progress_callback: Optional[Callable[[ProcessingProgress], None]] = None
    ) -> List[ContentState]:
        """
        Process multiple content items in batch with optional progress tracking.
        
        Args:
            content_list: List of content states to process.
            progress_callback: Optional callback for progress updates.
            
        Returns:
            List of processed content states.
        """
        if not content_list:
            return []
        
        logger.info(f"Starting batch processing of {len(content_list)} items")
        
        # Initialize progress tracking
        with self._progress_lock:
            self._current_progress = ProcessingProgress(
                total_items=len(content_list),
                completed_items=0,
                failed_items=0,
                retried_items=0,
                circuit_breaker_rejected=0,
                current_status="starting"
            )
            # Create a copy for the callback to avoid race conditions
            initial_progress = ProcessingProgress(
                total_items=self._current_progress.total_items,
                completed_items=self._current_progress.completed_items,
                failed_items=self._current_progress.failed_items,
                retried_items=self._current_progress.retried_items,
                circuit_breaker_rejected=self._current_progress.circuit_breaker_rejected,
                current_status=self._current_progress.current_status,
                start_time=self._current_progress.start_time
            )
        
        if progress_callback:
            progress_callback(initial_progress)
        
        results = []
        
        # Process items with thread pool for concurrency
        with ThreadPoolExecutor(max_workers=self.config.max_concurrent_jobs) as executor:
            # Submit all tasks
            future_to_content = {
                executor.submit(self.process_content, content): i 
                for i, content in enumerate(content_list)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_content):
                if self._stop_requested:
                    logger.info("Processing stopped by user request")
                    break
                
                content_index = future_to_content[future]
                
                try:
                    result = future.result(timeout=self.config.timeout_seconds)
                    results.append((content_index, result))
                    
                    # Update progress
                    with self._progress_lock:
                        if result.get("status") == "failed":
                            self._current_progress.failed_items += 1
                        else:
                            self._current_progress.completed_items += 1
                        
                        self._current_progress.update_status(
                            f"Processed {self._current_progress.completed_items + self._current_progress.failed_items}/{self._current_progress.total_items}"
                        )
                        
                        # Create a copy for the callback to avoid race conditions
                        progress_copy = ProcessingProgress(
                            total_items=self._current_progress.total_items,
                            completed_items=self._current_progress.completed_items,
                            failed_items=self._current_progress.failed_items,
                            retried_items=self._current_progress.retried_items,
                            circuit_breaker_rejected=self._current_progress.circuit_breaker_rejected,
                            current_status=self._current_progress.current_status,
                            start_time=self._current_progress.start_time
                        )
                    
                    if progress_callback:
                        progress_callback(progress_copy)
                        
                except Exception as e:
                    logger.error(f"Failed to process content at index {content_index}: {e}")
                    # Create failed result
                    failed_result = content_list[content_index].copy()
                    failed_result["status"] = "failed"
                    failed_result["error_message"] = str(e)
                    failed_result["error_type"] = "timeout"
                    failed_result["processed_at"] = datetime.now(timezone.utc).isoformat()
                    results.append((content_index, failed_result))
                    
                    with self._progress_lock:
                        self._current_progress.failed_items += 1
        
        # Sort results by original index and extract content states
        results.sort(key=lambda x: x[0])
        final_results = [result for _, result in results]
        
        # Final progress update
        with self._progress_lock:
            self._current_progress.update_status("completed")
            final_progress = ProcessingProgress(
                total_items=self._current_progress.total_items,
                completed_items=self._current_progress.completed_items,
                failed_items=self._current_progress.failed_items,
                retried_items=self._current_progress.retried_items,
                circuit_breaker_rejected=self._current_progress.circuit_breaker_rejected,
                current_status=self._current_progress.current_status,
                start_time=self._current_progress.start_time
            )
        
        if progress_callback:
            progress_callback(final_progress)
        
        logger.info(f"Batch processing completed. Successful: {self._current_progress.completed_items}, "
                   f"Failed: {self._current_progress.failed_items}, "
                   f"Retries: {self._current_progress.retried_items}, "
                   f"Circuit breaker rejections: {self._current_progress.circuit_breaker_rejected}")
        
        return final_results
    
    def get_processing_status(self) -> ProcessingProgress:
        """
        Get the current processing status.
        
        Returns:
            Current processing progress with thread-safe access.
        """
        with self._progress_lock:
            return ProcessingProgress(
                total_items=self._current_progress.total_items,
                completed_items=self._current_progress.completed_items,
                failed_items=self._current_progress.failed_items,
                retried_items=self._current_progress.retried_items,
                circuit_breaker_rejected=self._current_progress.circuit_breaker_rejected,
                current_status=self._current_progress.current_status,
                start_time=self._current_progress.start_time
            )
    
    def stop_processing(self) -> None:
        """
        Request to stop processing gracefully.
        
        This sets a flag that will be checked during batch processing
        to stop accepting new work.
        """
        self._stop_requested = True
        logger.info("Stop processing requested")
    
    def reset_stop_flag(self) -> None:
        """Reset the stop flag to allow processing to continue."""
        self._stop_requested = False
        logger.info("Stop flag reset, processing can continue")
    
    def get_circuit_breaker_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the status of all circuit breakers.
        
        Returns:
            Dictionary with circuit breaker statuses.
        """
        status = {}
        for name, cb in self.circuit_breakers.items():
            with cb._lock:
                status[name] = {
                    "state": cb.state.value,
                    "failure_count": cb.failure_count,
                    "last_failure_time": cb.last_failure_time.isoformat() if cb.last_failure_time else None,
                    "half_open_calls": cb.half_open_calls if cb.state == CircuitBreakerState.HALF_OPEN else 0
                }
        return status
    
    def reset_circuit_breakers(self) -> None:
        """Reset all circuit breakers to closed state."""
        for cb in self.circuit_breakers.values():
            with cb._lock:
                cb.state = CircuitBreakerState.CLOSED
                cb.failure_count = 0
                cb.last_failure_time = None
                cb.half_open_calls = 0
        logger.info("All circuit breakers reset to CLOSED state") 