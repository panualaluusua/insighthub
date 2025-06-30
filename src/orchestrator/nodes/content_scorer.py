"""
Content scoring node for the orchestrator pipeline.

This module implements the ContentScorer class that analyzes processed content
and assigns relevance scores based on multiple criteria including content quality,
engagement metrics, recency, source credibility, and content length.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import math
import re
from ..state import ContentState


class ContentScorer:
    """
    Content scoring node that evaluates content relevance using multiple criteria.
    
    Scoring criteria:
    - Content quality: Based on summary analysis and content structure
    - Engagement metrics: Views, likes, comments, upvotes (platform-specific)
    - Recency: Exponential decay for older content
    - Source credibility: Channel/subreddit reputation indicators
    - Content length: Optimization for ideal content length
    """
    
    def __init__(self, scoring_weights: Optional[Dict[str, float]] = None):
        """
        Initialize ContentScorer with scoring weights.
        
        Args:
            scoring_weights: Dictionary of scoring criteria weights.
                           If None, uses default balanced weights.
        """
        self.weights = scoring_weights or {
            "content_quality": 0.3,
            "engagement_metrics": 0.2,
            "recency": 0.15,
            "source_credibility": 0.2,
            "content_length": 0.15
        }
    
    def __call__(self, state: ContentState) -> ContentState:
        """
        Score content and add relevance_score to state.
        
        Args:
            state: ContentState containing processed content data
            
        Returns:
            ContentState with added relevance_score field
        """
        # Calculate individual scoring components
        quality_score = self._score_content_quality(state)
        engagement_score = self._score_engagement_metrics(state)
        recency_score = self._score_recency(state)
        credibility_score = self._score_source_credibility(state)
        length_score = self._score_content_length(state)
        
        # Calculate weighted final score
        relevance_score = (
            quality_score * self.weights["content_quality"] +
            engagement_score * self.weights["engagement_metrics"] +
            recency_score * self.weights["recency"] +
            credibility_score * self.weights["source_credibility"] +
            length_score * self.weights["content_length"]
        )
        
        # Ensure score is normalized to 0-1 range
        relevance_score = max(0.0, min(1.0, relevance_score))
        
        return {
            **state,
            "relevance_score": relevance_score
        }
    
    def _score_content_quality(self, state: ContentState) -> float:
        """
        Score content quality based on summary analysis and structure.
        
        Args:
            state: ContentState containing content data
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        summary = state.get("summary")
        if not summary:
            return 0.3  # Default low score for missing summary
        
        # Analyze summary characteristics
        quality_indicators = 0.0
        
        # Length indicates depth (but not too verbose)
        summary_length = len(summary)
        if 50 <= summary_length <= 500:
            quality_indicators += 0.4
        elif summary_length > 20:
            quality_indicators += 0.2
        
        # Look for educational/informative keywords
        educational_keywords = [
            "tutorial", "guide", "learn", "explain", "how to", "introduction",
            "comprehensive", "detailed", "analysis", "review", "comparison"
        ]
        summary_lower = summary.lower()
        keyword_matches = sum(1 for keyword in educational_keywords if keyword in summary_lower)
        quality_indicators += min(0.4, keyword_matches * 0.2)
        
        # Sentence structure (proper punctuation, capitalization)
        if summary[0].isupper() and ('.' in summary or '!' in summary or '?' in summary):
            quality_indicators += 0.2
        
        # Avoid clickbait indicators
        clickbait_words = ["shocking", "unbelievable", "you won't believe", "amazing trick"]
        if not any(word in summary_lower for word in clickbait_words):
            quality_indicators += 0.1
        
        return min(1.0, quality_indicators)
    
    def _score_engagement_metrics(self, state: ContentState) -> float:
        """
        Score engagement metrics based on platform-specific data.
        
        Args:
            state: ContentState containing metadata with engagement data
            
        Returns:
            Engagement score between 0.0 and 1.0
        """
        metadata = state.get("metadata", {})
        source_type = state.get("source_type", "")
        
        if source_type == "youtube":
            return self._score_youtube_engagement(metadata)
        elif source_type == "reddit":
            return self._score_reddit_engagement(metadata)
        else:
            return 0.5  # Default neutral score for unknown platforms
    
    def _score_youtube_engagement(self, metadata: Dict[str, Any]) -> float:
        """Score YouTube-specific engagement metrics."""
        view_count = metadata.get("view_count", 0)
        like_count = metadata.get("like_count", 0)
        
        # Simple scoring based on view and like counts
        view_score = min(1.0, math.log10(max(view_count, 1)) / 6)
        like_score = min(1.0, math.log10(max(like_count, 1)) / 4)
        
        return (view_score + like_score) / 2
    
    def _score_reddit_engagement(self, metadata: Dict[str, Any]) -> float:
        """Score Reddit-specific engagement metrics."""
        score = metadata.get("score", 0)
        num_comments = metadata.get("num_comments", 0)
        
        # Score based on upvotes and comment engagement
        upvote_score = min(1.0, math.log10(max(score, 1)) / 3)  # Log scale up to 1000 upvotes
        comment_score = min(1.0, math.log10(max(num_comments, 1)) / 2)  # Log scale up to 100 comments
        
        return (upvote_score + comment_score) / 2
    
    def _score_recency(self, state: ContentState) -> float:
        """
        Score content recency with exponential decay for older content.
        
        Args:
            state: ContentState containing metadata with publication date
            
        Returns:
            Recency score between 0.0 and 1.0
        """
        metadata = state.get("metadata", {})
        
        # Try to get publication date from various possible fields
        pub_date_str = (
            metadata.get("published_at") or 
            metadata.get("created_utc") or 
            state.get("created_at")
        )
        
        if not pub_date_str:
            return 0.5  # Default neutral score if no date available
        
        try:
            # Parse the date string
            if isinstance(pub_date_str, str):
                if pub_date_str.endswith('Z'):
                    pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                else:
                    pub_date = datetime.fromisoformat(pub_date_str)
            else:
                return 0.5
            
            # Calculate days since publication
            now = datetime.now(timezone.utc)
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)
            
            days_old = (now - pub_date).days
            
            # Exponential decay: score = e^(-days/30)
            # This gives ~37% score after 30 days, ~14% after 60 days
            recency_score = math.exp(-days_old / 30.0)
            
            return min(1.0, recency_score)
            
        except (ValueError, TypeError):
            return 0.5  # Default if date parsing fails
    
    def _score_source_credibility(self, state: ContentState) -> float:
        """
        Score source credibility based on channel/subreddit indicators.
        
        Args:
            state: ContentState containing source metadata
            
        Returns:
            Credibility score between 0.0 and 1.0
        """
        metadata = state.get("metadata", {})
        source_type = state.get("source_type", "")
        
        if source_type == "youtube":
            channel_name = metadata.get("channel_name", "").lower()
            credible_indicators = ["tech", "education", "tutorial", "programming"]
            
            credibility_score = 0.5
            for indicator in credible_indicators:
                if indicator in channel_name:
                    credibility_score += 0.1
            
            return min(1.0, credibility_score)
            
        elif source_type == "reddit":
            subreddit = metadata.get("subreddit", "").lower()
            quality_subreddits = ["programming", "python", "technology"]
            
            if subreddit in quality_subreddits:
                return 0.8
            elif subreddit:
                return 0.6
            else:
                return 0.4
        
        return 0.5
    
    def _score_content_length(self, state: ContentState) -> float:
        """
        Score content length optimization.
        
        Args:
            state: ContentState containing content data
            
        Returns:
            Length score between 0.0 and 1.0
        """
        raw_content = state.get("raw_content", "")
        metadata = state.get("metadata", {})
        
        # For YouTube, use duration; for text content, use character count
        if state.get("source_type") == "youtube":
            duration = metadata.get("duration", 0)
            if duration == 0:
                return 0.5
            
            # Optimal range: 5-30 minutes (300-1800 seconds)
            if 300 <= duration <= 1800:
                return 1.0
            elif duration < 120:  # Too short (< 2 minutes)
                return 0.3
            elif duration > 3600:  # Too long (> 1 hour)
                return 0.5
            else:
                return 0.7
        
        else:
            # For text content, use character count
            content_length = len(raw_content) if raw_content else 0
            
            # Optimal range: 500-3000 characters
            if 500 <= content_length <= 3000:
                return 1.0
            elif content_length < 200:  # Too short
                return 0.3
            elif content_length > 8000:  # Too long
                return 0.5
            else:
                return 0.7 