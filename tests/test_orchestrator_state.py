"""Unit tests for the orchestrator state schema and helper functions."""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.orchestrator.state import (
    ContentState,
    YouTubeMetadata,
    RedditMetadata,
    ProcessingConfig,
    BatchProcessingState,
    create_content_state,
    update_state_status,
    increment_retry_count,
    ContentMetadata,
    ProcessingStatus,
    SourceType,
)


class TestContentState:
    """Test cases for ContentState TypedDict and related functionality."""

    def test_create_content_state_youtube(self):
        """Test creating a ContentState for YouTube content."""
        source_url = "https://youtube.com/watch?v=test123"
        content_id = "test123"
        metadata = {"title": "Test Video"}
        
        state = create_content_state(
            source_type="youtube",
            source_url=source_url,
            content_id=content_id,
            metadata=metadata
        )
        
        assert state["source_type"] == "youtube"
        assert state["source_url"] == source_url
        assert state["content_id"] == content_id
        assert state["status"] == "pending"
        assert state["retry_count"] == 0
        assert state["metadata"] == metadata
        assert state["raw_content"] is None
        assert state["processed_content"] is None
        assert state["summary"] is None
        assert state["embeddings"] is None
        assert state["error_message"] is None
        assert state["current_node"] is None
        assert state["completed_at"] is None
        
        # Check timestamps are set
        assert state["created_at"] is not None
        assert state["updated_at"] is not None
        
        # Verify timestamp format (ISO format)
        datetime.fromisoformat(state["created_at"])
        datetime.fromisoformat(state["updated_at"])

    def test_create_content_state_reddit(self):
        """Test creating a ContentState for Reddit content."""
        source_url = "https://reddit.com/r/programming/comments/abc123/test"
        content_id = "abc123"
        
        state = create_content_state(
            source_type="reddit",
            source_url=source_url,
            content_id=content_id
        )
        
        assert state["source_type"] == "reddit"
        assert state["source_url"] == source_url
        assert state["content_id"] == content_id
        assert state["status"] == "pending"
        assert state["metadata"] == {}

    def test_create_content_state_minimal(self):
        """Test creating ContentState with minimal parameters."""
        state = create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=minimal"
        )
        
        assert state["source_type"] == "youtube"
        assert state["source_url"] == "https://youtube.com/watch?v=minimal"
        assert state["content_id"] is None
        assert state["metadata"] == {}

    def test_update_state_status_basic(self):
        """Test updating state status."""
        state = create_content_state("youtube", "https://test.com")
        original_created_at = state["created_at"]
        original_updated_at = state["updated_at"]
        
        updated_state = update_state_status(
            state,
            status="processing",
            current_node="fetch"
        )
        
        assert updated_state["status"] == "processing"
        assert updated_state["current_node"] == "fetch"
        assert updated_state["created_at"] == original_created_at  # Should not change
        assert updated_state["updated_at"] != original_updated_at  # Should change
        assert updated_state["completed_at"] is None

    def test_update_state_status_completed(self):
        """Test updating state to completed status sets completed_at."""
        state = create_content_state("reddit", "https://test.com")
        
        updated_state = update_state_status(
            state,
            status="completed",
            current_node="store"
        )
        
        assert updated_state["status"] == "completed"
        assert updated_state["current_node"] == "store"
        assert updated_state["completed_at"] is not None
        
        # Verify completed_at timestamp format
        datetime.fromisoformat(updated_state["completed_at"])

    def test_update_state_status_failed(self):
        """Test updating state to failed status with error message."""
        state = create_content_state("youtube", "https://test.com")
        error_msg = "Network timeout occurred"
        
        updated_state = update_state_status(
            state,
            status="failed",
            current_node="fetch",
            error_message=error_msg
        )
        
        assert updated_state["status"] == "failed"
        assert updated_state["current_node"] == "fetch"
        assert updated_state["error_message"] == error_msg

    def test_update_state_status_immutability(self):
        """Test that update_state_status doesn't mutate the original state."""
        original_state = create_content_state("youtube", "https://test.com")
        original_status = original_state["status"]
        
        updated_state = update_state_status(original_state, status="processing")
        
        # Original state should remain unchanged
        assert original_state["status"] == original_status
        assert updated_state["status"] == "processing"
        assert original_state is not updated_state

    def test_increment_retry_count(self):
        """Test incrementing retry count."""
        state = create_content_state("reddit", "https://test.com")
        original_updated_at = state["updated_at"]
        
        updated_state = increment_retry_count(state)
        
        assert updated_state["retry_count"] == 1
        assert updated_state["updated_at"] != original_updated_at
        assert state["retry_count"] == 0  # Original should be unchanged

    def test_increment_retry_count_multiple(self):
        """Test incrementing retry count multiple times."""
        state = create_content_state("youtube", "https://test.com")
        
        state = increment_retry_count(state)
        state = increment_retry_count(state)
        state = increment_retry_count(state)
        
        assert state["retry_count"] == 3


class TestMetadataStructures:
    """Test cases for metadata TypedDict structures."""

    def test_youtube_metadata_structure(self):
        """Test YouTubeMetadata structure."""
        metadata: YouTubeMetadata = {
            "video_id": "test123",
            "title": "Test Video",
            "duration": 300.5,
            "transcript_method": "whisper",
            "whisper_model": "tiny",
            "language": "en",
            "channel": "Test Channel",
            "upload_date": "2024-01-01"
        }
        
        assert metadata["video_id"] == "test123"
        assert metadata["transcript_method"] == "whisper"
        assert metadata["duration"] == 300.5

    def test_reddit_metadata_structure(self):
        """Test RedditMetadata structure."""
        metadata: RedditMetadata = {
            "post_id": "abc123",
            "subreddit": "programming",
            "title": "Test Post",
            "author": "testuser",
            "score": 150,
            "num_comments": 25,
            "created_utc": 1640995200.0,
            "permalink": "/r/programming/comments/abc123/test/",
            "is_self": True,
            "link_flair_text": "Discussion",
            "included_comments": 5,
            "sort_type": "hot",
            "time_filter": "day"
        }
        
        assert metadata["post_id"] == "abc123"
        assert metadata["subreddit"] == "programming"
        assert metadata["score"] == 150
        assert metadata["is_self"] is True

    def test_processing_config_structure(self):
        """Test ProcessingConfig structure."""
        config: ProcessingConfig = {
            "youtube_whisper_model": "base",
            "reddit_comment_limit": 10,
            "reddit_include_comments": True,
            "summarization_model": "claude-3-sonnet",
            "max_summary_length": 500,
            "summary_style": "detailed",
            "embedding_model": "text-embedding-ada-002",
            "embedding_dimensions": 1536,
            "max_retries": 3,
            "retry_delay": 2.0,
            "timeout": 30.0
        }
        
        assert config["youtube_whisper_model"] == "base"
        assert config["reddit_comment_limit"] == 10
        assert config["summary_style"] == "detailed"
        assert config["max_retries"] == 3

    def test_batch_processing_state_structure(self):
        """Test BatchProcessingState structure."""
        config: ProcessingConfig = {
            "youtube_whisper_model": "tiny",
            "reddit_comment_limit": 5,
            "reddit_include_comments": True,
            "summarization_model": "claude-3-sonnet",
            "max_summary_length": 300,
            "summary_style": "brief",
            "embedding_model": "text-embedding-ada-002",
            "embedding_dimensions": 1536,
            "max_retries": 2,
            "retry_delay": 1.0,
            "timeout": 15.0
        }
        
        batch_state: BatchProcessingState = {
            "batch_id": "batch_001",
            "total_items": 5,
            "processed_items": 3,
            "failed_items": 1,
            "status": "processing",
            "items": [],
            "config": config,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:05:00"
        }
        
        assert batch_state["batch_id"] == "batch_001"
        assert batch_state["total_items"] == 5
        assert batch_state["status"] == "processing"


class TestTypeAliases:
    """Test cases for type aliases."""

    def test_source_type_alias(self):
        """Test SourceType alias works correctly."""
        youtube_type: SourceType = "youtube"
        reddit_type: SourceType = "reddit"
        
        assert youtube_type == "youtube"
        assert reddit_type == "reddit"

    def test_processing_status_alias(self):
        """Test ProcessingStatus alias works correctly."""
        pending: ProcessingStatus = "pending"
        processing: ProcessingStatus = "processing"
        completed: ProcessingStatus = "completed"
        failed: ProcessingStatus = "failed"
        
        assert pending == "pending"
        assert processing == "processing"
        assert completed == "completed"
        assert failed == "failed"


if __name__ == "__main__":
    pytest.main([__file__]) 