"""Tests for error handling functionality in the orchestrator."""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta

from src.orchestrator.main import (
    Orchestrator, 
    OrchestratorConfig, 
    RetryConfig, 
    CircuitBreakerConfig,
    ErrorClassifier,
    ErrorType,
    RetryStrategy,
    CircuitBreaker,
    CircuitBreakerState,
    RetryManager
)
from src.orchestrator.state import ContentState, create_content_state


class TestErrorClassifier:
    """Test error classification functionality."""
    
    def test_classify_network_error(self):
        """Test classification of network errors."""
        error = ConnectionError("Network connection failed")
        assert ErrorClassifier.classify_error(error) == ErrorType.NETWORK
    
    def test_classify_timeout_error(self):
        """Test classification of timeout errors."""
        error = TimeoutError("Request timed out")
        assert ErrorClassifier.classify_error(error) == ErrorType.TIMEOUT
    
    def test_classify_rate_limit_error(self):
        """Test classification of rate limit errors."""
        error = Exception("Rate limit exceeded: 429 Too Many Requests")
        assert ErrorClassifier.classify_error(error) == ErrorType.RATE_LIMITED
    
    def test_classify_permanent_error(self):
        """Test classification of permanent errors."""
        error = Exception("401 Unauthorized access")
        assert ErrorClassifier.classify_error(error) == ErrorType.PERMANENT
    
    def test_classify_transient_error(self):
        """Test classification of transient server errors."""
        error = Exception("500 Internal Server Error")
        assert ErrorClassifier.classify_error(error) == ErrorType.TRANSIENT
    
    def test_classify_unknown_error(self):
        """Test classification of unknown errors."""
        error = Exception("Some unknown error")
        assert ErrorClassifier.classify_error(error) == ErrorType.UNKNOWN


class TestRetryManager:
    """Test retry management functionality."""
    
    def test_retry_manager_initialization(self):
        """Test RetryManager initializes with correct defaults."""
        config = RetryConfig()
        retry_manager = RetryManager(config)
        
        assert retry_manager.config.max_retries == 3
        assert retry_manager.config.base_delay == 1.0
        assert retry_manager.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF
    
    def test_should_retry_transient_error(self):
        """Test retry logic for transient errors."""
        config = RetryConfig(max_retries=3)
        retry_manager = RetryManager(config)
        
        error = Exception("500 Internal Server Error")
        
        # Should retry on first few attempts
        assert retry_manager.should_retry(error, 0) == True
        assert retry_manager.should_retry(error, 1) == True
        assert retry_manager.should_retry(error, 2) == True
        
        # Should not retry after max attempts
        assert retry_manager.should_retry(error, 3) == False
    
    def test_should_not_retry_permanent_error(self):
        """Test that permanent errors are not retried."""
        config = RetryConfig(max_retries=3)
        retry_manager = RetryManager(config)
        
        error = Exception("401 Unauthorized")
        
        # Should never retry permanent errors
        assert retry_manager.should_retry(error, 0) == False
        assert retry_manager.should_retry(error, 1) == False
    
    def test_exponential_backoff_delay(self):
        """Test exponential backoff delay calculation."""
        config = RetryConfig(
            base_delay=1.0,
            backoff_multiplier=2.0,
            jitter_enabled=False
        )
        retry_manager = RetryManager(config)
        
        # Test exponential backoff progression
        assert retry_manager.calculate_delay(0) == 1.0  # 1.0 * 2^0
        assert retry_manager.calculate_delay(1) == 2.0  # 1.0 * 2^1
        assert retry_manager.calculate_delay(2) == 4.0  # 1.0 * 2^2
    
    def test_max_delay_limit(self):
        """Test that delay is capped at max_delay."""
        config = RetryConfig(
            base_delay=1.0,
            max_delay=5.0,
            backoff_multiplier=2.0,
            jitter_enabled=False
        )
        retry_manager = RetryManager(config)
        
        # Large attempt should be capped at max_delay
        assert retry_manager.calculate_delay(10) == 5.0
    
    def test_fixed_delay_strategy(self):
        """Test fixed delay strategy."""
        config = RetryConfig(
            base_delay=2.0,
            strategy=RetryStrategy.FIXED_DELAY,
            jitter_enabled=False
        )
        retry_manager = RetryManager(config)
        
        # All attempts should have same delay
        assert retry_manager.calculate_delay(0) == 2.0
        assert retry_manager.calculate_delay(1) == 2.0
        assert retry_manager.calculate_delay(5) == 2.0
    
    def test_linear_backoff_strategy(self):
        """Test linear backoff strategy."""
        config = RetryConfig(
            base_delay=1.0,
            strategy=RetryStrategy.LINEAR_BACKOFF,
            jitter_enabled=False
        )
        retry_manager = RetryManager(config)
        
        # Linear progression
        assert retry_manager.calculate_delay(0) == 1.0  # 1.0 * (0 + 1)
        assert retry_manager.calculate_delay(1) == 2.0  # 1.0 * (1 + 1)
        assert retry_manager.calculate_delay(2) == 3.0  # 1.0 * (2 + 1)


class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    def test_circuit_breaker_initialization(self):
        """Test CircuitBreaker initializes with correct defaults."""
        cb = CircuitBreaker("test_service")
        
        assert cb.service_name == "test_service"
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert cb.can_execute() == True
    
    def test_circuit_breaker_open_after_failures(self):
        """Test circuit breaker opens after threshold failures."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker("test_service", config)
        
        # Should allow execution initially
        assert cb.can_execute() == True
        
        # Record failures
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.can_execute() == True
        
        # Third failure should open circuit
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.can_execute() == False
    
    def test_circuit_breaker_half_open_transition(self):
        """Test circuit breaker transitions to half-open after timeout."""
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=0.1)
        cb = CircuitBreaker("test_service", config)
        
        # Open the circuit
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        
        # Should not execute immediately
        assert cb.can_execute() == False
        
        # Wait for recovery timeout
        time.sleep(0.2)
        
        # Should transition to half-open
        assert cb.can_execute() == True
        assert cb.state == CircuitBreakerState.HALF_OPEN
    
    def test_circuit_breaker_close_after_success(self):
        """Test circuit breaker closes after successful operations in half-open."""
        config = CircuitBreakerConfig(failure_threshold=2, half_open_max_calls=2)
        cb = CircuitBreaker("test_service", config)
        
        # Open the circuit
        cb.record_failure()
        cb.record_failure()
        cb.state = CircuitBreakerState.HALF_OPEN  # Manually set for test
        
        # Record successful operations
        cb.record_success()
        assert cb.state == CircuitBreakerState.HALF_OPEN
        
        cb.record_success()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0


class TestOrchestratorErrorHandling:
    """Test orchestrator error handling integration."""
    
    @pytest.fixture
    def error_config(self):
        """Create orchestrator config with error handling enabled."""
        retry_config = RetryConfig(max_retries=2, base_delay=0.1, jitter_enabled=False)
        circuit_config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=0.1)
        
        return OrchestratorConfig(
            max_concurrent_jobs=2,
            retry_config=retry_config,
            circuit_breaker_config=circuit_config,
            enable_circuit_breaker=True
        )
    
    @pytest.fixture
    def sample_content_state(self):
        """Create a sample ContentState for testing."""
        return create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test123"
        )
    
    def test_orchestrator_retry_on_transient_error(self, error_config, sample_content_state):
        """Test that orchestrator retries on transient errors."""
        with patch('src.orchestrator.main.create_orchestrator_graph') as mock_graph_factory:
            mock_graph = Mock()
            mock_graph_factory.return_value = mock_graph
            
            # First call fails, second succeeds
            mock_graph.invoke.side_effect = [
                Exception("500 Internal Server Error"),
                sample_content_state
            ]
            
            orchestrator = Orchestrator(error_config)
            result = orchestrator.process_content(sample_content_state)
            
            # Should have retried once and succeeded
            assert mock_graph.invoke.call_count == 2
            assert result == sample_content_state
    
    def test_orchestrator_no_retry_on_permanent_error(self, error_config, sample_content_state):
        """Test that orchestrator doesn't retry permanent errors."""
        with patch('src.orchestrator.main.create_orchestrator_graph') as mock_graph_factory:
            mock_graph = Mock()
            mock_graph_factory.return_value = mock_graph
            
            # Permanent error
            mock_graph.invoke.side_effect = Exception("401 Unauthorized")
            
            orchestrator = Orchestrator(error_config)
            result = orchestrator.process_content(sample_content_state)
            
            # Should not have retried
            assert mock_graph.invoke.call_count == 1
            assert result["status"] == "failed"
            assert "401 Unauthorized" in result["error_message"]
            assert result["error_type"] == "permanent"
    
    def test_orchestrator_circuit_breaker_opens(self, error_config, sample_content_state):
        """Test that circuit breaker opens after repeated failures."""
        with patch('src.orchestrator.main.create_orchestrator_graph') as mock_graph_factory:
            mock_graph = Mock()
            mock_graph_factory.return_value = mock_graph
            
            # Always fail
            mock_graph.invoke.side_effect = Exception("500 Internal Server Error")
            
            orchestrator = Orchestrator(error_config)
            
            # Process multiple items to trigger circuit breaker
            for i in range(5):
                result = orchestrator.process_content(sample_content_state)
                assert result["status"] == "failed"
            
            # Circuit breaker should now be open
            cb_status = orchestrator.get_circuit_breaker_status()
            assert cb_status["graph_processing"]["state"] == "open"
            
            # Next request should be rejected immediately
            result = orchestrator.process_content(sample_content_state)
            assert result["status"] == "failed"
            assert result["error_type"] == "circuit_breaker"
    
    def test_orchestrator_circuit_breaker_recovery(self, error_config, sample_content_state):
        """Test circuit breaker recovery after timeout."""
        with patch('src.orchestrator.main.create_orchestrator_graph') as mock_graph_factory:
            mock_graph = Mock()
            mock_graph_factory.return_value = mock_graph
            
            orchestrator = Orchestrator(error_config)
            
            # Manually open circuit breaker
            cb = orchestrator.circuit_breakers["graph_processing"]
            cb.state = CircuitBreakerState.OPEN
            cb.failure_count = 5
            cb.last_failure_time = datetime.now(timezone.utc) - timedelta(seconds=1)
            
            # Mock successful response
            mock_graph.invoke.return_value = sample_content_state
            
            # Should allow execution after timeout
            result = orchestrator.process_content(sample_content_state)
            assert result == sample_content_state
            
            # Circuit breaker should be in half-open state
            assert cb.state == CircuitBreakerState.HALF_OPEN
    
    def test_orchestrator_progress_tracking_with_retries(self, error_config):
        """Test that progress tracking includes retry information."""
        with patch('src.orchestrator.main.create_orchestrator_graph') as mock_graph_factory:
            mock_graph = Mock()
            mock_graph_factory.return_value = mock_graph
            
            # Create sample content
            content_list = [
                create_content_state(source_type="youtube", source_url=f"https://youtube.com/watch?v=test{i}")
                for i in range(3)
            ]
            
            # First item fails once then succeeds, others succeed immediately
            mock_graph.invoke.side_effect = [
                Exception("500 Internal Server Error"),  # First attempt fails
                content_list[0],  # Retry succeeds
                content_list[1],  # Second item succeeds
                content_list[2]   # Third item succeeds
            ]
            
            orchestrator = Orchestrator(error_config)
            
            progress_updates = []
            def progress_callback(progress):
                progress_updates.append(progress)
            
            results = orchestrator.process_batch(content_list, progress_callback)
            
            # Should have processed all items
            assert len(results) == 3
            assert all(result["status"] != "failed" for result in results)
            
            # Should have recorded retry information
            final_progress = orchestrator.get_processing_status()
            assert final_progress.retried_items > 0
            assert final_progress.completed_items == 3
            assert final_progress.failed_items == 0
    
    def test_orchestrator_circuit_breaker_status(self, error_config):
        """Test circuit breaker status reporting."""
        orchestrator = Orchestrator(error_config)
        
        status = orchestrator.get_circuit_breaker_status()
        assert "graph_processing" in status
        assert status["graph_processing"]["state"] == "closed"
        assert status["graph_processing"]["failure_count"] == 0
    
    def test_orchestrator_reset_circuit_breakers(self, error_config):
        """Test circuit breaker reset functionality."""
        orchestrator = Orchestrator(error_config)
        
        # Manually set circuit breaker to open state
        cb = orchestrator.circuit_breakers["graph_processing"]
        cb.state = CircuitBreakerState.OPEN
        cb.failure_count = 5
        
        # Reset circuit breakers
        orchestrator.reset_circuit_breakers()
        
        # Should be reset to closed state
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
    
    def test_orchestrator_batch_processing_with_circuit_breaker(self, error_config):
        """Test batch processing with circuit breaker rejections."""
        with patch('src.orchestrator.main.create_orchestrator_graph') as mock_graph_factory:
            mock_graph = Mock()
            mock_graph_factory.return_value = mock_graph
            
            # Always fail to trigger circuit breaker
            mock_graph.invoke.side_effect = Exception("500 Internal Server Error")
            
            content_list = [
                create_content_state(source_type="youtube", source_url=f"https://youtube.com/watch?v=test{i}")
                for i in range(10)
            ]
            
            orchestrator = Orchestrator(error_config)
            results = orchestrator.process_batch(content_list)
            
            # All should have failed
            assert len(results) == 10
            assert all(result["status"] == "failed" for result in results)
            
            # Some should be circuit breaker rejections
            final_progress = orchestrator.get_processing_status()
            assert final_progress.circuit_breaker_rejected > 0
    
    def test_error_handling_with_custom_retry_config(self, sample_content_state):
        """Test error handling with custom retry configuration."""
        custom_retry_config = RetryConfig(
            max_retries=1,
            base_delay=0.05,
            strategy=RetryStrategy.FIXED_DELAY,
            jitter_enabled=False
        )
        
        config = OrchestratorConfig(retry_config=custom_retry_config)
        
        with patch('src.orchestrator.main.create_orchestrator_graph') as mock_graph_factory:
            mock_graph = Mock()
            mock_graph_factory.return_value = mock_graph
            
            # Always fail
            mock_graph.invoke.side_effect = Exception("Network error")
            
            orchestrator = Orchestrator(config)
            
            start_time = time.time()
            result = orchestrator.process_content(sample_content_state)
            end_time = time.time()
            
            # Should have retried once with fixed delay
            assert mock_graph.invoke.call_count == 2
            assert result["status"] == "failed"
            assert result["retry_count"] == 1
            
            # Should have taken approximately the delay time
            assert end_time - start_time >= 0.05 