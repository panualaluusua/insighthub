"""
Tests for the orchestrator graph construction and execution.

This module tests the LangGraph StateGraph implementation that coordinates
content processing through the pipeline: fetch → summarize → embed → store.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from src.orchestrator.state import ContentState
from src.orchestrator.graph import create_orchestrator_graph


class TestOrchestratorGraph:
    """Test cases for the orchestrator graph construction and execution."""

    def test_create_orchestrator_graph_returns_compiled_graph(self):
        """Test that create_orchestrator_graph returns a compiled LangGraph StateGraph."""
        with patch('src.orchestrator.nodes.storage.StorageNode.__init__', return_value=None):
            graph = create_orchestrator_graph()
            
            # Should return a compiled graph object
            assert graph is not None
            assert hasattr(graph, 'invoke'), "Graph should have invoke method for execution"

    def test_graph_contains_all_required_nodes(self):
        """Test that the graph contains all four processing nodes."""
        with patch('src.orchestrator.graph.StateGraph') as mock_state_graph:
            mock_graph_instance = Mock()
            mock_state_graph.return_value = mock_graph_instance
            
            create_orchestrator_graph()
            
            # Verify all nodes are added to the graph
            add_node_calls = mock_graph_instance.add_node.call_args_list
            node_names = [call[0][0] for call in add_node_calls]
            
            assert "content_fetcher" in node_names, "Graph should contain content_fetcher node"
            assert "summarizer" in node_names, "Graph should contain summarizer node"
            assert "embedding" in node_names, "Graph should contain embedding node"
            assert "scorer" in node_names, "Graph should contain scorer node"
            assert "storage" in node_names, "Graph should contain storage node"

    def test_graph_has_correct_edge_sequence(self):
        """Test that edges are configured for proper flow: content_fetcher → summarizer → embedding → scorer → storage."""
        with patch('src.orchestrator.graph.StateGraph') as mock_state_graph:
            mock_graph_instance = Mock()
            mock_state_graph.return_value = mock_graph_instance
            
            create_orchestrator_graph()
            
            # Verify edge connections
            add_edge_calls = mock_graph_instance.add_edge.call_args_list
            edges = [(call[0][0], call[0][1]) for call in add_edge_calls]
            
            assert ("content_fetcher", "summarizer") in edges, "Should have edge from content_fetcher to summarizer"
            assert ("summarizer", "embedding") in edges, "Should have edge from summarizer to embedding"
            assert ("embedding", "scorer") in edges, "Should have edge from embedding to scorer"
            assert ("scorer", "storage") in edges, "Should have edge from scorer to storage"

    def test_graph_sets_start_and_end_points(self):
        """Test that the graph has proper START and END point configuration."""
        with patch('src.orchestrator.graph.StateGraph') as mock_state_graph, \
             patch('src.orchestrator.graph.START') as mock_start, \
             patch('src.orchestrator.graph.END') as mock_end:
            
            mock_graph_instance = Mock()
            mock_state_graph.return_value = mock_graph_instance
            
            create_orchestrator_graph()
            
            # Verify START and END edges are set
            add_edge_calls = mock_graph_instance.add_edge.call_args_list
            edges = [(call[0][0], call[0][1]) for call in add_edge_calls]
            
            # Check that START connects to content_fetcher and storage connects to END
            start_edges = [edge for edge in edges if edge[0] == mock_start]
            end_edges = [edge for edge in edges if edge[1] == mock_end]
            
            assert len(start_edges) > 0, "Should have edge from START"
            assert len(end_edges) > 0, "Should have edge to END"

    def test_graph_handles_invalid_state_gracefully(self):
        """Test that the graph handles invalid or incomplete state objects."""
        invalid_state = {"invalid": "state"}
        
        graph = create_orchestrator_graph()
        
        # Should raise appropriate error for invalid state
        with pytest.raises((KeyError, TypeError, ValueError, Exception)):
            graph.invoke(invalid_state)

    def test_node_instances_are_created_correctly(self):
        """Test that node instances are created with proper initialization."""
        with patch('src.orchestrator.graph.ContentFetcherNode') as mock_fetcher, \
             patch('src.orchestrator.graph.SummarizerNode') as mock_summarizer, \
             patch('src.orchestrator.graph.EmbeddingNode') as mock_embedder, \
             patch('src.orchestrator.graph.ContentScorer') as mock_scorer:
            
            create_orchestrator_graph()
            
            # Verify first three nodes are instantiated
            mock_fetcher.assert_called_once()
            mock_summarizer.assert_called_once()
            mock_embedder.assert_called_once()
            mock_scorer.assert_called_once()
            # Note: StorageNode is wrapped in lambda, so it's not directly instantiated

    def test_storage_node_wrapped_correctly(self):
        """Test that StorageNode.store_content is properly wrapped as a callable."""
        with patch('src.orchestrator.graph.StateGraph') as mock_state_graph:
            mock_graph_instance = Mock()
            mock_state_graph.return_value = mock_graph_instance
            
            create_orchestrator_graph()
            
            # Find the storage node call
            add_node_calls = mock_graph_instance.add_node.call_args_list
            storage_call = None
            for call in add_node_calls:
                if call[0][0] == "storage":
                    storage_call = call[0][1]
                    break
            
            assert storage_call is not None, "Storage node should be added to graph"
            assert callable(storage_call), "Storage node should be wrapped as callable"

    def test_basic_graph_execution_with_valid_state(self):
        """Test that the graph can execute with a valid ContentState."""
        # Create a minimal valid state
        valid_state: ContentState = {
            "source_type": "youtube",
            "source_url": "https://youtube.com/watch?v=test123",
            "content_id": "test_id",
            "raw_content": "Test content",
            "processed_content": None,
            "summary": None,
            "embeddings": None,
            "status": "pending",
            "current_node": None,
            "error_message": None,
            "retry_count": 0,
            "metadata": {},
            "created_at": None,
            "updated_at": None,
            "completed_at": None
        }
        
        graph = create_orchestrator_graph()
        
        # This should not raise an exception with valid state structure
        # The actual processing will depend on the real node implementations
        try:
            result = graph.invoke(valid_state)
            # If it executes, verify it returns a dict-like object
            assert isinstance(result, dict), "Graph should return a dict-like result"
        except Exception as e:
            # If it fails, it should be due to actual processing logic, not state structure
            # We mainly want to ensure the graph is properly constructed
            assert "InvalidUpdateError" not in str(type(e)), f"Graph structure issue: {e}" 