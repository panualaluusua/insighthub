"""Tests for the StorageNode.

Following TDD approach - these tests should FAIL initially, then we'll implement the StorageNode.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import json

from src.orchestrator.nodes.storage import StorageNode
from src.orchestrator.state import ContentState, create_content_state


class TestStorageNode:
    """Test cases for StorageNode database persistence."""

    @pytest.fixture
    def mock_supabase_client(self):
        """Mock Supabase client for testing."""
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        
        # Mock successful insert
        mock_response = Mock()
        mock_response.data = [{"id": "test-content-id", "status": "completed"}]
        mock_response.error = None
        mock_table.insert.return_value.execute.return_value = mock_response
        
        # Mock successful update
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_response
        
        # Mock successful select
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        
        return mock_client

    @pytest.fixture
    def sample_content_state(self):
        """Sample ContentState for testing."""
        state = create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test123",
            content_id="test123",
            metadata={"title": "Test Video", "duration": 300}
        )
        # Manually set additional fields that would be set by processing nodes
        state["raw_content"] = "This is test content"
        state["processed_content"] = "This is processed test content"
        state["summary"] = "Test summary"
        state["embeddings"] = [0.1, 0.2, 0.3]
        state["status"] = "completed"
        return state

    @pytest.fixture
    def storage_node(self, mock_supabase_client):
        """StorageNode instance with mocked Supabase client."""
        with patch('src.orchestrator.nodes.storage.supabase_client') as mock_client_module:
            mock_client_module.get_client.return_value = mock_supabase_client
            return StorageNode()

    def test_storage_node_initialization(self, mock_supabase_client):
        """Test that StorageNode initializes properly with Supabase client."""
        with patch('src.orchestrator.nodes.storage.supabase_client') as mock_client_module:
            mock_client_module.get_client.return_value = mock_supabase_client
            
            node = StorageNode()
            
            assert node.client == mock_supabase_client
            assert node.table_name == "content"
            mock_client_module.get_client.assert_called_once()

    def test_storage_node_initialization_without_client(self):
        """Test that StorageNode raises error when Supabase client is unavailable."""
        with patch('src.orchestrator.nodes.storage.supabase_client') as mock_client_module:
            mock_client_module.get_client.return_value = None
            
            with pytest.raises(ValueError, match="Supabase client not available"):
                StorageNode()

    def test_lazy_loading_initialization(self):
        """Test that StorageNode uses lazy loading pattern."""
        # Should not raise error during import/class definition
        from src.orchestrator.nodes.storage import StorageNode
        assert StorageNode is not None

    def test_store_content_success(self, storage_node, sample_content_state, mock_supabase_client):
        """Test successful content storage."""
        mock_response = Mock()
        mock_response.data = [{"id": "stored-content-id"}]
        mock_response.error = None
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        result = storage_node.store_content(sample_content_state)
        
        # Verify the response
        assert result["status"] == "completed"
        assert result["content_id"] == "test123"
        assert "stored_at" in result
        
        # Verify Supabase calls
        mock_supabase_client.table.assert_called_with("content")
        mock_supabase_client.table.return_value.insert.assert_called_once()
        
        # Verify the data structure passed to insert
        insert_call_args = mock_supabase_client.table.return_value.insert.call_args[0][0]
        assert insert_call_args["source_type"] == "youtube"
        assert insert_call_args["source_url"] == "https://youtube.com/watch?v=test123"
        assert insert_call_args["content_id"] == "test123"
        assert insert_call_args["raw_content"] == "This is test content"
        assert insert_call_args["summary"] == "Test summary"
        assert insert_call_args["embeddings"] == [0.1, 0.2, 0.3]

    def test_store_content_database_error(self, storage_node, sample_content_state, mock_supabase_client):
        """Test handling of database errors during storage."""
        mock_response = Mock()
        mock_response.data = None
        mock_response.error = {"message": "Database error", "code": "42P01"}
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        with pytest.raises(Exception, match="Failed to store content"):
            storage_node.store_content(sample_content_state)

    def test_store_content_missing_required_fields(self, storage_node):
        """Test error handling for missing required fields."""
        incomplete_state = {
            "source_type": "youtube",
            # Missing required fields
        }
        
        with pytest.raises(KeyError):
            storage_node.store_content(incomplete_state)

    def test_update_content_status(self, storage_node, mock_supabase_client):
        """Test updating content status in database."""
        mock_response = Mock()
        mock_response.data = [{"id": "test123", "status": "completed"}]
        mock_response.error = None
        mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        
        result = storage_node.update_status("test123", "completed")
        
        assert result["content_id"] == "test123"
        assert result["status"] == "completed"
        assert "updated_at" in result
        
        mock_supabase_client.table.assert_called_with("content")
        # Check that update was called with status and updated_at
        update_call_args = mock_supabase_client.table.return_value.update.call_args[0][0]
        assert update_call_args["status"] == "completed"
        assert "updated_at" in update_call_args
        mock_supabase_client.table.return_value.update.return_value.eq.assert_called_with("content_id", "test123")

    def test_retrieve_content(self, storage_node, mock_supabase_client):
        """Test retrieving content from database."""
        mock_response = Mock()
        mock_response.data = {
            "content_id": "test123",
            "source_type": "youtube",
            "summary": "Test summary",
            "status": "completed"
        }
        mock_response.error = None
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        
        result = storage_node.get_content("test123")
        
        assert result["content_id"] == "test123"
        assert result["source_type"] == "youtube"
        assert result["summary"] == "Test summary"
        
        mock_supabase_client.table.assert_called_with("content")
        mock_supabase_client.table.return_value.select.assert_called_with("*")
        mock_supabase_client.table.return_value.select.return_value.eq.assert_called_with("content_id", "test123")

    def test_retrieve_nonexistent_content(self, storage_node, mock_supabase_client):
        """Test retrieving content that doesn't exist."""
        mock_response = Mock()
        mock_response.data = None
        mock_response.error = {"message": "No rows found", "code": "PGRST116"}
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        
        result = storage_node.get_content("nonexistent")
        
        assert result is None

    def test_batch_store_content(self, storage_node, mock_supabase_client):
        """Test storing multiple content items in batch."""
        content_states = [
            create_content_state("youtube", "https://youtube.com/watch?v=1", "1"),
            create_content_state("reddit", "https://reddit.com/r/test/comments/2", "2"),
        ]
        
        mock_response = Mock()
        mock_response.data = [
            {"id": "1", "content_id": "1"},
            {"id": "2", "content_id": "2"}
        ]
        mock_response.error = None
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        results = storage_node.batch_store(content_states)
        
        assert len(results) == 2
        assert all(r["status"] == "completed" for r in results)
        
        # Verify batch insert call
        mock_supabase_client.table.return_value.insert.assert_called_once()
        insert_data = mock_supabase_client.table.return_value.insert.call_args[0][0]
        assert len(insert_data) == 2

    def test_get_content_by_source_url(self, storage_node, mock_supabase_client):
        """Test retrieving content by source URL."""
        mock_response = Mock()
        mock_response.data = [{"content_id": "test123", "source_url": "https://example.com"}]
        mock_response.error = None
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        results = storage_node.get_content_by_source_url("https://example.com")
        
        assert len(results) == 1
        assert results[0]["content_id"] == "test123"
        
        mock_supabase_client.table.return_value.select.return_value.eq.assert_called_with("source_url", "https://example.com")

    def test_prepare_content_for_storage(self, storage_node, sample_content_state):
        """Test content preparation for database storage."""
        prepared = storage_node._prepare_content_for_storage(sample_content_state)
        
        # Should include all required fields
        assert "source_type" in prepared
        assert "source_url" in prepared
        assert "content_id" in prepared
        assert "raw_content" in prepared
        assert "summary" in prepared
        assert "embeddings" in prepared
        assert "metadata" in prepared
        assert "status" in prepared
        assert "created_at" in prepared
        
        # Metadata should be JSON string
        assert isinstance(prepared["metadata"], str)
        metadata = json.loads(prepared["metadata"])
        assert metadata["title"] == "Test Video"

    def test_handle_storage_error_gracefully(self, storage_node, sample_content_state, mock_supabase_client):
        """Test graceful error handling during storage operations."""
        # Simulate connection error
        mock_supabase_client.table.side_effect = Exception("Connection timeout")
        
        with pytest.raises(Exception, match="Storage operation failed"):
            storage_node.store_content(sample_content_state) 