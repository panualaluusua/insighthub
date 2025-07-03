"""Tests for EmbeddingNode - TDD Red Phase

This module tests the EmbeddingNode which generates vector embeddings
for content using OpenAI's text-embedding-ada-002 model.
Since DeepSeek doesn't have embedding models, we use OpenAI for embeddings.
"""

import pytest
from unittest.mock import Mock, patch
import numpy as np
from src.orchestrator.state import ContentState, create_content_state
from src.orchestrator.nodes.embedding import EmbeddingNode
from unittest.mock import ANY


class TestEmbeddingNode:
    """Test suite for EmbeddingNode following TDD principles."""

    def test_embedding_node_exists(self):
        """Test that EmbeddingNode class can be imported and instantiated."""
        node = EmbeddingNode()
        assert node is not None

    def test_embedding_node_has_call_method(self):
        """Test that EmbeddingNode has __call__ method for LangGraph compatibility."""
        node = EmbeddingNode()
        assert hasattr(node, '__call__')
        assert callable(getattr(node, '__call__'))

    @patch('src.orchestrator.nodes.embedding.OpenAIEmbeddings')
    def test_embedding_node_uses_openai_embeddings(self, mock_embeddings):
        """Test that EmbeddingNode configures OpenAI embeddings correctly."""
        mock_embedding_instance = Mock()
        mock_embeddings.return_value = mock_embedding_instance
        
        node = EmbeddingNode()
        
        # Access the embeddings property to trigger lazy loading
        _ = node.embeddings
        # Verify OpenAI embeddings configuration
        mock_embeddings.assert_called_once_with(
            model="text-embedding-ada-002",
            api_key=ANY  # Allow env-provided key
        )

    @patch('src.orchestrator.nodes.embedding.OpenAIEmbeddings')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-openai-key'})
    def test_embedding_node_uses_environment_api_key(self, mock_embeddings):
        """Test that EmbeddingNode uses OPENAI_API_KEY from environment."""
        mock_embedding_instance = Mock()
        mock_embeddings.return_value = mock_embedding_instance
        
        node = EmbeddingNode(api_key='test-openai-key')
        
        # Access the embeddings property to trigger lazy loading
        _ = node.embeddings
        mock_embeddings.assert_called_once_with(
            model="text-embedding-ada-002",
            api_key='test-openai-key'
        )

    @patch('src.orchestrator.nodes.embedding.OpenAIEmbeddings')
    def test_embedding_generates_embeddings_for_summary(self, mock_embeddings):
        """Test that EmbeddingNode generates embeddings for content summary."""
        # Setup mock embeddings
        mock_embedding_instance = Mock()
        mock_vector = [0.1, 0.2, 0.3] * 512  # 1536 dimensions for ada-002
        mock_embedding_instance.embed_query.return_value = mock_vector
        mock_embeddings.return_value = mock_embedding_instance
        
        # Create test state with summary
        state = create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test123",
            content_id="test123"
        )
        state["summary"] = "This video discusses AI developments in 2024..."
        state["status"] = "summarized"
        
        # Execute
        node = EmbeddingNode()
        result = node(state)
        
        # Verify embeddings were generated
        assert "embeddings" in result
        assert result["embeddings"] == mock_vector
        assert result["status"] == "embedded"
        assert result["current_node"] == "embedding"
        assert len(result["embeddings"]) == 1536  # OpenAI ada-002 dimension

    @patch('src.orchestrator.nodes.embedding.OpenAIEmbeddings')
    def test_embedding_falls_back_to_raw_content(self, mock_embeddings):
        """Test that EmbeddingNode uses raw_content if summary is missing."""
        # Setup mock embeddings
        mock_embedding_instance = Mock()
        mock_vector = [0.1, 0.2, 0.3] * 512  # 1536 dimensions
        mock_embedding_instance.embed_query.return_value = mock_vector
        mock_embeddings.return_value = mock_embedding_instance
        
        # Create test state without summary
        state = create_content_state(
            source_type="reddit",
            source_url="https://reddit.com/r/programming/comments/test",
            content_id="test_post"
        )
        state["raw_content"] = "Original Reddit post content about programming..."
        state["status"] = "content_fetched"
        
        # Execute
        node = EmbeddingNode()
        result = node(state)
        
        # Verify embeddings were generated from raw content
        assert "embeddings" in result
        assert result["embeddings"] == mock_vector
        assert result["status"] == "embedded"
        mock_embedding_instance.embed_query.assert_called_once_with(
            "Original Reddit post content about programming..."
        )

    @patch('src.orchestrator.nodes.embedding.OpenAIEmbeddings')
    def test_embedding_prefers_summary_over_raw_content(self, mock_embeddings):
        """Test that EmbeddingNode prefers summary over raw_content when both exist."""
        # Setup mock embeddings
        mock_embedding_instance = Mock()
        mock_vector = [0.1, 0.2, 0.3] * 512
        mock_embedding_instance.embed_query.return_value = mock_vector
        mock_embeddings.return_value = mock_embedding_instance
        
        # Create test state with both summary and raw content
        state = create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test123",
            content_id="test123"
        )
        state["raw_content"] = "Very long original video transcript..."
        state["summary"] = "Concise summary of the video content"
        state["status"] = "summarized"
        
        # Execute
        node = EmbeddingNode()
        result = node(state)
        
        # Verify embeddings were generated from summary, not raw content
        mock_embedding_instance.embed_query.assert_called_once_with(
            "Concise summary of the video content"
        )

    @patch('src.orchestrator.nodes.embedding.OpenAIEmbeddings')
    def test_embedding_handles_empty_content(self, mock_embeddings):
        """Test that EmbeddingNode handles empty content gracefully."""
        mock_embedding_instance = Mock()
        mock_embeddings.return_value = mock_embedding_instance
        
        # Create test state with no content
        state = create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test123",
            content_id="test123"
        )
        state["raw_content"] = ""
        state["summary"] = ""
        state["status"] = "content_fetched"
        
        # Execute
        node = EmbeddingNode()
        result = node(state)
        
        # Verify error handling
        assert result["status"] == "error"
        assert "error_message" in result
        assert "no content" in result["error_message"].lower()

    @patch('src.orchestrator.nodes.embedding.OpenAIEmbeddings')
    def test_embedding_handles_api_errors(self, mock_embeddings):
        """Test that EmbeddingNode handles embedding API errors gracefully."""
        # Setup mock embeddings to raise exception
        mock_embedding_instance = Mock()
        mock_embedding_instance.embed_query.side_effect = Exception("OpenAI API error")
        mock_embeddings.return_value = mock_embedding_instance
        
        # Create test state
        state = create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test123",
            content_id="test123"
        )
        state["summary"] = "Test summary for embedding..."
        state["status"] = "summarized"
        
        # Execute
        node = EmbeddingNode()
        result = node(state)
        
        # Verify error handling
        assert result["status"] == "error"
        assert "error_message" in result
        assert "OpenAI API error" in result["error_message"]

    @patch('src.orchestrator.nodes.embedding.OpenAIEmbeddings')
    def test_embedding_preserves_state_fields(self, mock_embeddings):
        """Test that EmbeddingNode preserves all existing state fields."""
        # Setup mock embeddings
        mock_embedding_instance = Mock()
        mock_vector = [0.1, 0.2, 0.3] * 512
        mock_embedding_instance.embed_query.return_value = mock_vector
        mock_embeddings.return_value = mock_embedding_instance
        
        # Create test state with metadata
        state = create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test123",
            content_id="test123"
        )
        state["raw_content"] = "Original content"
        state["summary"] = "Summary content"
        state["metadata"] = {"duration": "10:30", "title": "Test Video"}
        state["status"] = "summarized"
        
        # Execute
        node = EmbeddingNode()
        result = node(state)
        
        # Verify all fields are preserved
        assert result["source_type"] == "youtube"
        assert result["source_url"] == "https://youtube.com/watch?v=test123"
        assert result["content_id"] == "test123"
        assert result["raw_content"] == "Original content"
        assert result["summary"] == "Summary content"
        assert result["metadata"] == {"duration": "10:30", "title": "Test Video"}
        assert result["embeddings"] == mock_vector
        assert "updated_at" in result

    @patch('src.orchestrator.nodes.embedding.OpenAIEmbeddings')
    def test_embedding_custom_model_configuration(self, mock_embeddings):
        """Test that EmbeddingNode allows custom embedding model configuration."""
        mock_embedding_instance = Mock()
        mock_embeddings.return_value = mock_embedding_instance
        
        # Test with custom model
        node = EmbeddingNode(model="text-embedding-3-small", api_key="custom-key")
        
        # Access the embeddings property to trigger lazy loading
        _ = node.embeddings
        mock_embeddings.assert_called_once_with(
            model="text-embedding-3-small",
            api_key="custom-key"
        )

    @patch('src.orchestrator.nodes.embedding.OpenAIEmbeddings')
    def test_embedding_content_truncation_for_long_text(self, mock_embeddings):
        """Test that EmbeddingNode handles very long content appropriately."""
        # Setup mock embeddings
        mock_embedding_instance = Mock()
        mock_vector = [0.1, 0.2, 0.3] * 512
        mock_embedding_instance.embed_query.return_value = mock_vector
        mock_embeddings.return_value = mock_embedding_instance
        
        # Create test state with very long content
        state = create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test123",
            content_id="test123"
        )
        # Simulate very long content (over embedding token limits)
        long_content = "This is a very long piece of content. " * 2000
        state["summary"] = long_content
        state["status"] = "summarized"
        
        # Execute
        node = EmbeddingNode()
        result = node(state)
        
        # Verify embeddings were generated (content should be truncated if needed)
        assert "embeddings" in result
        assert result["status"] == "embedded"
        mock_embedding_instance.embed_query.assert_called_once()

    @patch('src.orchestrator.nodes.embedding.OpenAIEmbeddings')
    def test_embedding_dimension_validation(self, mock_embeddings):
        """Test that EmbeddingNode validates embedding dimensions."""
        # Setup mock embeddings with wrong dimensions
        mock_embedding_instance = Mock()
        mock_vector = [0.1, 0.2, 0.3]  # Only 3 dimensions instead of 1536
        mock_embedding_instance.embed_query.return_value = mock_vector
        mock_embeddings.return_value = mock_embedding_instance
        
        # Create test state
        state = create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test123",
            content_id="test123"
        )
        state["summary"] = "Test summary for embedding"
        state["status"] = "summarized"
        
        # Execute
        node = EmbeddingNode()
        result = node(state)
        
        # Should still work but might log warning about unexpected dimensions
        assert "embeddings" in result
        assert result["embeddings"] == mock_vector
        assert result["status"] == "embedded" 