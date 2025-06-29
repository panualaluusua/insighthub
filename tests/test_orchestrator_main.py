"""Tests for the main Orchestrator class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Callable, Optional, Any
from datetime import datetime, timezone

# Import the class to test (will fail until implemented)
from src.orchestrator.main import Orchestrator, OrchestratorConfig, ProcessingProgress

# Import dependencies
from src.orchestrator.state import ContentState, create_content_state


class TestOrchestratorConfig:
    """Test the OrchestratorConfig class."""
    
    def test_config_creation_with_defaults(self):
        """Test that OrchestratorConfig can be created with default values."""
        config = OrchestratorConfig()
        assert config.max_concurrent_jobs == 5
        assert config.timeout_seconds == 300
        assert config.max_retries == 3
        assert config.enable_progress_tracking is True
        
    def test_config_creation_with_custom_values(self):
        """Test that OrchestratorConfig can be created with custom values."""
        config = OrchestratorConfig(
            max_concurrent_jobs=10,
            timeout_seconds=600,
            max_retries=5,
            enable_progress_tracking=False
        )
        assert config.max_concurrent_jobs == 10
        assert config.timeout_seconds == 600
        assert config.max_retries == 5
        assert config.enable_progress_tracking is False


class TestProcessingProgress:
    """Test the ProcessingProgress class."""
    
    def test_progress_creation(self):
        """Test that ProcessingProgress can be created and tracks status."""
        progress = ProcessingProgress(
            total_items=10,
            completed_items=3,
            failed_items=1,
            current_status="Processing item 4"
        )
        assert progress.total_items == 10
        assert progress.completed_items == 3
        assert progress.failed_items == 1
        assert progress.current_status == "Processing item 4"
        assert progress.completion_percentage == 30.0
        
    def test_progress_completion_percentage(self):
        """Test completion percentage calculation."""
        progress = ProcessingProgress(total_items=0, completed_items=0, failed_items=0)
        assert progress.completion_percentage == 0.0
        
        progress = ProcessingProgress(total_items=100, completed_items=50, failed_items=10)
        assert progress.completion_percentage == 50.0


class TestOrchestrator:
    """Test the main Orchestrator class."""
    
    @pytest.fixture
    def mock_graph(self):
        """Create a mock StateGraph for testing."""
        mock = Mock()
        completed_state = create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test"
        )
        completed_state["status"] = "completed"
        mock.invoke.return_value = completed_state
        return mock
    
    @pytest.fixture
    def sample_content_state(self):
        """Create a sample ContentState for testing."""
        return create_content_state(
            source_type="youtube", 
            source_url="https://youtube.com/watch?v=test123"
        )
    
    @pytest.fixture
    def sample_content_batch(self):
        """Create a sample batch of ContentState objects for testing."""
        return [
            create_content_state(
                source_type="youtube",
                source_url=f"https://youtube.com/watch?v=test{i}"
            )
            for i in range(5)
        ]
    
    def test_orchestrator_instantiation_default_config(self):
        """Test that Orchestrator can be instantiated with default configuration."""
        orchestrator = Orchestrator()
        assert orchestrator.config.max_concurrent_jobs == 5
        assert orchestrator.config.timeout_seconds == 300
        assert orchestrator.graph is not None
        
    def test_orchestrator_instantiation_custom_config(self):
        """Test that Orchestrator can be instantiated with custom configuration."""
        config = OrchestratorConfig(max_concurrent_jobs=10, timeout_seconds=600)
        orchestrator = Orchestrator(config=config)
        assert orchestrator.config.max_concurrent_jobs == 10
        assert orchestrator.config.timeout_seconds == 600
        
    @patch('src.orchestrator.main.create_orchestrator_graph')
    def test_orchestrator_uses_graph_from_factory(self, mock_create_graph, mock_graph):
        """Test that Orchestrator uses the graph from create_orchestrator_graph."""
        mock_create_graph.return_value = mock_graph
        orchestrator = Orchestrator()
        assert orchestrator.graph == mock_graph
        mock_create_graph.assert_called_once()
        
    def test_process_content_single_item(self, mock_graph, sample_content_state):
        """Test processing a single content item."""
        with patch('src.orchestrator.main.create_orchestrator_graph', return_value=mock_graph):
            orchestrator = Orchestrator()
            result = orchestrator.process_content(sample_content_state)
            
            assert result is not None
            assert result["status"] == "completed"
            mock_graph.invoke.assert_called_once_with(sample_content_state)
            
    def test_process_content_with_error_handling(self, sample_content_state):
        """Test that process_content handles errors gracefully."""
        mock_graph = Mock()
        mock_graph.invoke.side_effect = Exception("Graph processing failed")
        
        with patch('src.orchestrator.main.create_orchestrator_graph', return_value=mock_graph):
            orchestrator = Orchestrator()
            result = orchestrator.process_content(sample_content_state)
            
            assert result is not None
            assert result["status"] == "failed"
            assert "Graph processing failed" in result["error_message"]
            
    def test_process_batch_multiple_items(self, mock_graph, sample_content_batch):
        """Test processing multiple content items in batch."""
        with patch('src.orchestrator.main.create_orchestrator_graph', return_value=mock_graph):
            orchestrator = Orchestrator()
            results = orchestrator.process_batch(sample_content_batch)
            
            assert len(results) == 5
            assert all(result["status"] == "completed" for result in results)
            assert mock_graph.invoke.call_count == 5
            
    def test_process_batch_with_progress_callback(self, mock_graph, sample_content_batch):
        """Test batch processing with progress callback."""
        progress_updates = []
        
        def progress_callback(progress: ProcessingProgress):
            progress_updates.append(progress)
            
        with patch('src.orchestrator.main.create_orchestrator_graph', return_value=mock_graph):
            orchestrator = Orchestrator()
            results = orchestrator.process_batch(
                sample_content_batch, 
                progress_callback=progress_callback
            )
            
            assert len(results) == 5
            assert len(progress_updates) > 0
            # Should have at least start and end progress updates
            assert progress_updates[0].completed_items == 0
            assert progress_updates[-1].completed_items == 5
            
    def test_process_batch_with_partial_failures(self, sample_content_batch):
        """Test batch processing when some items fail."""
        mock_graph = Mock()
        # First 3 succeed, last 2 fail
        completed_state1 = create_content_state("youtube", "url1")
        completed_state1["status"] = "completed"
        completed_state2 = create_content_state("youtube", "url2")
        completed_state2["status"] = "completed"
        completed_state3 = create_content_state("youtube", "url3")
        completed_state3["status"] = "completed"
        
        mock_graph.invoke.side_effect = [
            completed_state1,
            completed_state2,
            completed_state3,
            Exception("Processing failed"),
            Exception("Another failure")
        ]
        
        with patch('src.orchestrator.main.create_orchestrator_graph', return_value=mock_graph):
            orchestrator = Orchestrator()
            results = orchestrator.process_batch(sample_content_batch)
            
            assert len(results) == 5
            completed = [r for r in results if r["status"] == "completed"]
            failed = [r for r in results if r["status"] == "failed"]
            assert len(completed) == 3
            assert len(failed) == 2
            
    def test_get_processing_status_idle(self):
        """Test getting processing status when orchestrator is idle."""
        with patch('src.orchestrator.main.create_orchestrator_graph'):
            orchestrator = Orchestrator()
            status = orchestrator.get_processing_status()
            
            assert status.total_items == 0
            assert status.completed_items == 0
            assert status.failed_items == 0
            assert status.current_status == "idle"
            
    def test_stop_processing(self, mock_graph):
        """Test stopping processing gracefully."""
        with patch('src.orchestrator.main.create_orchestrator_graph', return_value=mock_graph):
            orchestrator = Orchestrator()
            orchestrator.stop_processing()
            # Should not raise any errors and should set internal stop flag
            assert orchestrator._stop_requested is True
            
    def test_configuration_validation(self):
        """Test that invalid configuration raises appropriate errors."""
        with pytest.raises(ValueError, match="max_concurrent_jobs must be positive"):
            OrchestratorConfig(max_concurrent_jobs=0)
            
        with pytest.raises(ValueError, match="timeout_seconds must be positive"):
            OrchestratorConfig(timeout_seconds=-1)
            
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            OrchestratorConfig(max_retries=-1) 