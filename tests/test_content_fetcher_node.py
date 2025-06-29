"""Tests for ContentFetcherNode - TDD Red Phase

This module tests the ContentFetcherNode which routes content fetching
to appropriate processors based on source_type.
"""

import pytest
from unittest.mock import Mock, patch
from src.orchestrator.state import ContentState, create_content_state, YouTubeMetadata, RedditMetadata
from src.orchestrator.nodes.content_fetcher import ContentFetcherNode


class TestContentFetcherNode:
    """Test suite for ContentFetcherNode following TDD principles."""

    def test_content_fetcher_node_exists(self):
        """Test that ContentFetcherNode class can be imported and instantiated."""
        node = ContentFetcherNode()
        assert node is not None

    def test_content_fetcher_node_has_call_method(self):
        """Test that ContentFetcherNode has a __call__ method for LangGraph compatibility."""
        node = ContentFetcherNode()
        assert hasattr(node, '__call__')
        assert callable(getattr(node, '__call__'))

    @patch('src.orchestrator.nodes.content_fetcher.YouTubeProcessor')
    def test_routes_youtube_content_to_youtube_processor(self, mock_youtube_processor):
        """Test that YouTube URLs are routed to YouTubeProcessor."""
        # Setup
        mock_processor_instance = Mock()
        mock_processor_instance.get_video_id.return_value = "dQw4w9WgXcQ"
        mock_processor_instance.get_transcript.return_value = "Never gonna give you up, never gonna let you down..."
        mock_youtube_processor.return_value = mock_processor_instance

        node = ContentFetcherNode()
        state = create_content_state(
            source_type="youtube",
            source_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )

        # Execute
        result = node(state)

        # Assert
        assert result["source_type"] == "youtube"
        assert result["raw_content"] == "Never gonna give you up, never gonna let you down..."
        assert result["content_id"] == "dQw4w9WgXcQ"
        assert result["status"] == "processing"
        assert result["current_node"] == "content_fetcher"
        
        # Verify processor was called correctly
        mock_processor_instance.get_video_id.assert_called_once_with("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        mock_processor_instance.get_transcript.assert_called_once_with("https://www.youtube.com/watch?v=dQw4w9WgXcQ", model_size="base")

    @patch('src.orchestrator.nodes.content_fetcher.RedditProcessor')
    def test_routes_reddit_content_to_reddit_processor(self, mock_reddit_processor):
        """Test that Reddit URLs are routed to RedditProcessor."""
        # Setup mock Reddit processor
        mock_processor_instance = Mock()
        mock_reddit_post = Mock()
        mock_reddit_post.id = "test123"
        mock_reddit_post.title = "Test Post"
        mock_reddit_post.selftext = "This is a test post"
        mock_reddit_post.subreddit = "python"
        
        mock_processor_instance.fetch_posts.return_value = [mock_reddit_post]
        mock_processor_instance.process_post_content.return_value = "Processed Reddit content"
        mock_reddit_processor.return_value = mock_processor_instance

        node = ContentFetcherNode()
        state = create_content_state(
            source_type="reddit",
            source_url="https://www.reddit.com/r/python/comments/test123/test_post/"
        )

        # Execute
        result = node(state)

        # Assert
        assert result["source_type"] == "reddit"
        assert result["raw_content"] == "Processed Reddit content"
        assert result["content_id"] == "test123"
        assert result["status"] == "processing"
        assert result["current_node"] == "content_fetcher"
        
        # Verify metadata contains Reddit-specific information
        metadata = result["metadata"]
        assert isinstance(metadata, dict)
        assert metadata["post_id"] == "test123"
        assert metadata["subreddit"] == "python"

    def test_updates_state_with_youtube_metadata(self):
        """Test that YouTube content fetching includes proper metadata."""
        with patch('src.orchestrator.nodes.content_fetcher.YouTubeProcessor') as mock_youtube:
            # Setup
            mock_processor = Mock()
            mock_processor.get_video_id.return_value = "test_video_id"
            mock_processor.get_transcript.return_value = "Test transcript"
            mock_youtube.return_value = mock_processor

            node = ContentFetcherNode()
            state = create_content_state(
                source_type="youtube",
                source_url="https://www.youtube.com/watch?v=test_video_id"
            )

            # Execute
            result = node(state)

            # Assert metadata structure
            metadata = result["metadata"]
            assert "video_id" in metadata
            assert "transcript_method" in metadata
            assert "whisper_model" in metadata
            assert metadata["video_id"] == "test_video_id"
            assert metadata["transcript_method"] == "whisper"
            assert metadata["whisper_model"] == "base"

    def test_handles_youtube_processing_errors(self):
        """Test that YouTube processing errors are handled gracefully."""
        with patch('src.orchestrator.nodes.content_fetcher.YouTubeProcessor') as mock_youtube:
            # Setup mock to raise exception
            mock_processor = Mock()
            mock_processor.get_transcript.side_effect = ValueError("Failed to get transcript")
            mock_youtube.return_value = mock_processor

            node = ContentFetcherNode()
            state = create_content_state(
                source_type="youtube",
                source_url="https://www.youtube.com/watch?v=invalid_id"
            )

            # Execute
            result = node(state)

            # Assert error handling
            assert result["status"] == "failed"
            assert result["current_node"] == "content_fetcher"
            assert "Failed to get transcript" in result["error_message"]
            assert result["raw_content"] is None

    def test_handles_reddit_processing_errors(self):
        """Test that Reddit processing errors are handled gracefully."""
        with patch('src.orchestrator.nodes.content_fetcher.RedditProcessor') as mock_reddit:
            # Setup mock to raise exception
            mock_processor = Mock()
            mock_processor.fetch_posts.side_effect = ValueError("Subreddit not found")
            mock_reddit.return_value = mock_processor

            node = ContentFetcherNode()
            state = create_content_state(
                source_type="reddit",
                source_url="https://www.reddit.com/r/nonexistent/comments/test/"
            )

            # Execute
            result = node(state)

            # Assert error handling
            assert result["status"] == "failed"
            assert result["current_node"] == "content_fetcher"
            assert "Subreddit not found" in result["error_message"]
            assert result["raw_content"] is None

    def test_handles_invalid_source_type(self):
        """Test that invalid source types are handled gracefully."""
        node = ContentFetcherNode()
        # Create a state with invalid source_type (this would normally be prevented by typing)
        state = create_content_state(
            source_type="youtube",  # We'll modify it to be invalid
            source_url="https://example.com"
        )
        # Manually set invalid source type to test error handling
        state["source_type"] = "invalid"  # type: ignore

        # Execute
        result = node(state)

        # Assert error handling
        assert result["status"] == "failed"
        assert result["current_node"] == "content_fetcher"
        assert "Unsupported source type" in result["error_message"]

    def test_extracts_reddit_post_id_from_url(self):
        """Test that Reddit post IDs are correctly extracted from URLs."""
        with patch('src.orchestrator.nodes.content_fetcher.RedditProcessor') as mock_reddit:
            # Setup
            mock_processor = Mock()
            mock_post = Mock()
            mock_post.id = "extracted_id"
            mock_post.title = "Test"
            mock_post.selftext = "Content"
            mock_post.subreddit = "test"
            
            mock_processor.fetch_posts.return_value = [mock_post]
            mock_processor.process_post_content.return_value = "Content"
            mock_reddit.return_value = mock_processor

            node = ContentFetcherNode()
            
            # Test different Reddit URL formats
            test_urls = [
                "https://www.reddit.com/r/python/comments/abc123/test_post/",
                "https://reddit.com/r/python/comments/abc123/",
                "https://www.reddit.com/r/python/comments/abc123/test_post/?utm_source=share"
            ]
            
            for url in test_urls:
                state = create_content_state(source_type="reddit", source_url=url)
                result = node(state)
                
                # The content_id should be extracted from the URL or the fetched post
                assert result["content_id"] is not None

    def test_preserves_original_state_fields(self):
        """Test that the node preserves fields from the original state that shouldn't change."""
        with patch('src.orchestrator.nodes.content_fetcher.YouTubeProcessor') as mock_youtube:
            mock_processor = Mock()
            mock_processor.get_video_id.return_value = "test_id"
            mock_processor.get_transcript.return_value = "Test content"
            mock_youtube.return_value = mock_processor

            node = ContentFetcherNode()
            
            # Create state with existing fields
            state = create_content_state(
                source_type="youtube",
                source_url="https://www.youtube.com/watch?v=test_id"
            )
            original_created_at = state["created_at"]
            original_retry_count = state["retry_count"]

            # Execute
            result = node(state)

            # Assert preserved fields
            assert result["created_at"] == original_created_at
            assert result["retry_count"] == original_retry_count
            assert result["source_url"] == state["source_url"]

    def test_updates_timestamps_correctly(self):
        """Test that the node updates timestamps appropriately."""
        with patch('src.orchestrator.nodes.content_fetcher.YouTubeProcessor') as mock_youtube:
            mock_processor = Mock()
            mock_processor.get_video_id.return_value = "test_id"
            mock_processor.get_transcript.return_value = "Test content"
            mock_youtube.return_value = mock_processor

            node = ContentFetcherNode()
            state = create_content_state(
                source_type="youtube",
                source_url="https://www.youtube.com/watch?v=test_id"
            )
            original_updated_at = state["updated_at"]

            # Execute
            result = node(state)

            # Assert timestamps
            assert result["updated_at"] != original_updated_at  # Should be updated
            assert result["completed_at"] is None  # Should not be completed yet 