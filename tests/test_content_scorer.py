"""
Tests for the ContentScorer node.

This module tests the content scoring functionality that analyzes processed content
and assigns relevance scores based on multiple criteria including content quality,
engagement metrics, recency, source credibility, and content length.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from src.orchestrator.state import ContentState
from src.orchestrator.nodes.content_scorer import ContentScorer


class TestContentScorer:
    """Test cases for the ContentScorer node."""

    def test_content_scorer_initialization(self):
        """Test that ContentScorer initializes with default scoring weights."""
        scorer = ContentScorer()
        
        # Verify default weights are set
        assert scorer.weights is not None
        assert "content_quality" in scorer.weights
        assert "engagement_metrics" in scorer.weights
        assert "recency" in scorer.weights
        assert "source_credibility" in scorer.weights
        assert "content_length" in scorer.weights
        
        # Verify weights sum to reasonable total (around 1.0)
        total_weight = sum(scorer.weights.values())
        assert 0.9 <= total_weight <= 1.1, f"Weights should sum to ~1.0, got {total_weight}"

    def test_content_scorer_initialization_with_custom_weights(self):
        """Test ContentScorer initialization with custom scoring weights."""
        custom_weights = {
            "content_quality": 0.5,
            "engagement_metrics": 0.3,
            "recency": 0.2
        }
        
        scorer = ContentScorer(scoring_weights=custom_weights)
        
        assert scorer.weights == custom_weights

    def test_content_scorer_callable(self):
        """Test that ContentScorer implements __call__ method."""
        scorer = ContentScorer()
        assert callable(scorer), "ContentScorer should be callable"

    def test_score_content_with_youtube_content(self):
        """Test content scoring with YouTube content data."""
        scorer = ContentScorer()
        
        # Create YouTube content state
        content_state: ContentState = {
            "source_type": "youtube",
            "source_url": "https://youtube.com/watch?v=test123",
            "content_id": "test123",
            "raw_content": "This is a high-quality educational video about Python programming...",
            "processed_content": None,
            "summary": "Comprehensive tutorial on Python programming fundamentals",
            "embeddings": [0.1, 0.2, 0.3],
            "status": "completed",
            "current_node": "scorer",
            "error_message": None,
            "retry_count": 0,
            "metadata": {
                "title": "Python Programming Tutorial",
                "duration": 1800,  # 30 minutes
                "view_count": 50000,
                "like_count": 2500,
                "channel_name": "TechEducator",
                "published_at": "2025-06-28T10:00:00Z"
            },
            "created_at": "2025-06-29T10:00:00Z",
            "updated_at": "2025-06-29T10:30:00Z",
            "completed_at": None
        }
        
        result = scorer(content_state)
        
        # Verify score is added to state
        assert "relevance_score" in result
        assert isinstance(result["relevance_score"], (int, float))
        assert 0 <= result["relevance_score"] <= 1, "Score should be normalized to 0-1 range"
        
        # Verify other state fields are preserved
        assert result["source_type"] == content_state["source_type"]
        assert result["summary"] == content_state["summary"]

    def test_score_content_with_reddit_content(self):
        """Test content scoring with Reddit content data."""
        scorer = ContentScorer()
        
        # Create Reddit content state
        content_state: ContentState = {
            "source_type": "reddit",
            "source_url": "https://reddit.com/r/programming/comments/test123",
            "content_id": "test123",
            "raw_content": "Interesting discussion about new Python features...",
            "processed_content": None,
            "summary": "Discussion about Python 3.12 new features and improvements",
            "embeddings": [0.4, 0.5, 0.6],
            "status": "completed",
            "current_node": "scorer",
            "error_message": None,
            "retry_count": 0,
            "metadata": {
                "title": "Python 3.12 Features Discussion",
                "subreddit": "programming",
                "score": 150,
                "num_comments": 45,
                "author": "pythondev",
                "created_utc": "2025-06-28T15:00:00Z"
            },
            "created_at": "2025-06-29T10:00:00Z",
            "updated_at": "2025-06-29T10:30:00Z",
            "completed_at": None
        }
        
        result = scorer(content_state)
        
        # Verify score is added to state
        assert "relevance_score" in result
        assert isinstance(result["relevance_score"], (int, float))
        assert 0 <= result["relevance_score"] <= 1, "Score should be normalized to 0-1 range"

    def test_content_quality_scoring(self):
        """Test content quality scoring based on summary analysis."""
        scorer = ContentScorer()
        
        # Test high quality content
        high_quality_state: ContentState = {
            "source_type": "youtube",
            "source_url": "https://youtube.com/watch?v=test123",
            "content_id": "test123",
            "raw_content": "Detailed technical content...",
            "processed_content": None,
            "summary": "Comprehensive, well-structured tutorial covering advanced Python concepts with clear explanations and practical examples",
            "embeddings": [0.1, 0.2, 0.3],
            "status": "completed",
            "current_node": "scorer",
            "error_message": None,
            "retry_count": 0,
            "metadata": {"title": "Advanced Python Tutorial"},
            "created_at": "2025-06-29T10:00:00Z",
            "updated_at": "2025-06-29T10:30:00Z",
            "completed_at": None
        }
        
        # Test low quality content
        low_quality_state: ContentState = {
            **high_quality_state,
            "summary": "Short video. Ok."
        }
        
        high_score = scorer(high_quality_state)["relevance_score"]
        low_score = scorer(low_quality_state)["relevance_score"]
        
        assert high_score > low_score, "High quality content should score higher than low quality"

    def test_engagement_metrics_scoring(self):
        """Test engagement metrics scoring for different content types."""
        scorer = ContentScorer()
        
        # High engagement YouTube content
        high_engagement_youtube: ContentState = {
            "source_type": "youtube",
            "source_url": "https://youtube.com/watch?v=test123",
            "content_id": "test123",
            "raw_content": "Content...",
            "processed_content": None,
            "summary": "Tutorial content",
            "embeddings": [0.1, 0.2, 0.3],
            "status": "completed",
            "current_node": "scorer",
            "error_message": None,
            "retry_count": 0,
            "metadata": {
                "title": "Tutorial",
                "view_count": 100000,
                "like_count": 5000,
                "duration": 1200
            },
            "created_at": "2025-06-29T10:00:00Z",
            "updated_at": "2025-06-29T10:30:00Z",
            "completed_at": None
        }
        
        # Low engagement YouTube content
        low_engagement_youtube: ContentState = {
            **high_engagement_youtube,
            "metadata": {
                "title": "Tutorial",
                "view_count": 100,
                "like_count": 5,
                "duration": 1200
            }
        }
        
        high_score = scorer(high_engagement_youtube)["relevance_score"]
        low_score = scorer(low_engagement_youtube)["relevance_score"]
        
        assert high_score > low_score, "High engagement content should score higher"

    def test_recency_scoring(self):
        """Test recency scoring with exponential decay for older content."""
        scorer = ContentScorer()
        
        # Recent content
        recent_content: ContentState = {
            "source_type": "youtube",
            "source_url": "https://youtube.com/watch?v=test123",
            "content_id": "test123",
            "raw_content": "Content...",
            "processed_content": None,
            "summary": "Recent tutorial",
            "embeddings": [0.1, 0.2, 0.3],
            "status": "completed",
            "current_node": "scorer",
            "error_message": None,
            "retry_count": 0,
            "metadata": {
                "title": "Tutorial",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "view_count": 1000,
                "like_count": 50
            },
            "created_at": "2025-06-29T10:00:00Z",
            "updated_at": "2025-06-29T10:30:00Z",
            "completed_at": None
        }
        
        # Old content (1 year ago)
        old_content: ContentState = {
            **recent_content,
            "metadata": {
                **recent_content["metadata"],
                "published_at": (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()
            }
        }
        
        recent_score = scorer(recent_content)["relevance_score"]
        old_score = scorer(old_content)["relevance_score"]
        
        assert recent_score > old_score, "Recent content should score higher than old content"

    def test_content_length_optimization(self):
        """Test content length scoring that penalizes too short or too long content."""
        scorer = ContentScorer()
        
        # Optimal length content
        optimal_content: ContentState = {
            "source_type": "youtube",
            "source_url": "https://youtube.com/watch?v=test123",
            "content_id": "test123",
            "raw_content": "A" * 2000,  # Optimal length
            "processed_content": None,
            "summary": "Well-sized tutorial content",
            "embeddings": [0.1, 0.2, 0.3],
            "status": "completed",
            "current_node": "scorer",
            "error_message": None,
            "retry_count": 0,
            "metadata": {"title": "Tutorial", "duration": 900},  # 15 minutes
            "created_at": "2025-06-29T10:00:00Z",
            "updated_at": "2025-06-29T10:30:00Z",
            "completed_at": None
        }
        
        # Too short content
        short_content: ContentState = {
            **optimal_content,
            "raw_content": "A" * 100,  # Too short
            "metadata": {"title": "Tutorial", "duration": 60}  # 1 minute
        }
        
        # Too long content
        long_content: ContentState = {
            **optimal_content,
            "raw_content": "A" * 10000,  # Too long
            "metadata": {"title": "Tutorial", "duration": 7200}  # 2 hours
        }
        
        optimal_score = scorer(optimal_content)["relevance_score"]
        short_score = scorer(short_content)["relevance_score"]
        long_score = scorer(long_content)["relevance_score"]
        
        assert optimal_score > short_score, "Optimal length should score higher than too short"
        assert optimal_score > long_score, "Optimal length should score higher than too long"

    def test_score_normalization(self):
        """Test that scores are properly normalized to 0-1 range."""
        scorer = ContentScorer()
        
        # Test multiple content samples
        content_samples = []
        for i in range(10):
            content_state: ContentState = {
                "source_type": "youtube",
                "source_url": f"https://youtube.com/watch?v=test{i}",
                "content_id": f"test{i}",
                "raw_content": f"Content {i}...",
                "processed_content": None,
                "summary": f"Tutorial content {i}",
                "embeddings": [0.1, 0.2, 0.3],
                "status": "completed",
                "current_node": "scorer",
                "error_message": None,
                "retry_count": 0,
                "metadata": {
                    "title": f"Tutorial {i}",
                    "view_count": i * 1000,
                    "like_count": i * 50
                },
                "created_at": "2025-06-29T10:00:00Z",
                "updated_at": "2025-06-29T10:30:00Z",
                "completed_at": None
            }
            content_samples.append(content_state)
        
        scores = [scorer(content)["relevance_score"] for content in content_samples]
        
        # Verify all scores are in 0-1 range
        for score in scores:
            assert 0 <= score <= 1, f"Score {score} is outside 0-1 range"
        
        # Verify we have score variation (not all identical)
        assert len(set(scores)) > 1, "Scores should vary between different content"

    def test_missing_metadata_handling(self):
        """Test graceful handling of missing metadata fields."""
        scorer = ContentScorer()
        
        # Content with minimal metadata
        minimal_content: ContentState = {
            "source_type": "youtube",
            "source_url": "https://youtube.com/watch?v=test123",
            "content_id": "test123",
            "raw_content": "Content with minimal metadata",
            "processed_content": None,
            "summary": "Basic tutorial",
            "embeddings": [0.1, 0.2, 0.3],
            "status": "completed",
            "current_node": "scorer",
            "error_message": None,
            "retry_count": 0,
            "metadata": {"title": "Basic Tutorial"},  # Missing engagement metrics
            "created_at": "2025-06-29T10:00:00Z",
            "updated_at": "2025-06-29T10:30:00Z",
            "completed_at": None
        }
        
        # Should not raise exception
        result = scorer(minimal_content)
        
        assert "relevance_score" in result
        assert 0 <= result["relevance_score"] <= 1

    def test_state_preservation(self):
        """Test that ContentScorer preserves all original state fields."""
        scorer = ContentScorer()
        
        original_state: ContentState = {
            "source_type": "youtube",
            "source_url": "https://youtube.com/watch?v=test123",
            "content_id": "test123",
            "raw_content": "Original content",
            "processed_content": None,
            "summary": "Original summary",
            "embeddings": [0.1, 0.2, 0.3],
            "status": "completed",
            "current_node": "scorer",
            "error_message": None,
            "retry_count": 0,
            "metadata": {"title": "Original Title"},
            "created_at": "2025-06-29T10:00:00Z",
            "updated_at": "2025-06-29T10:30:00Z",
            "completed_at": None
        }
        
        result = scorer(original_state)
        
        # Verify all original fields are preserved
        for key, value in original_state.items():
            assert result[key] == value, f"Field {key} was modified"
        
        # Verify new field is added
        assert "relevance_score" in result
        assert "relevance_score" not in original_state

    def test_scorer_with_empty_summary(self):
        """Test scorer behavior with empty or None summary."""
        scorer = ContentScorer()
        
        empty_summary_state: ContentState = {
            "source_type": "youtube",
            "source_url": "https://youtube.com/watch?v=test123",
            "content_id": "test123",
            "raw_content": "Content without summary",
            "processed_content": None,
            "summary": None,
            "embeddings": [0.1, 0.2, 0.3],
            "status": "completed",
            "current_node": "scorer",
            "error_message": None,
            "retry_count": 0,
            "metadata": {"title": "No Summary"},
            "created_at": "2025-06-29T10:00:00Z",
            "updated_at": "2025-06-29T10:30:00Z",
            "completed_at": None
        }
        
        # Should handle gracefully
        result = scorer(empty_summary_state)
        
        assert "relevance_score" in result
        assert 0 <= result["relevance_score"] <= 1 