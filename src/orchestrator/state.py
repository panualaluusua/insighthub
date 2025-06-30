"""State schema definitions for the InsightHub content orchestrator.

This module defines the TypedDict schemas used by LangGraph to track
content processing state through the orchestration pipeline.
"""

from typing import TypedDict, List, Optional, Literal, Dict, Any, Union
from datetime import datetime, timezone


class ContentState(TypedDict):
    """Main state object for content processing through the LangGraph pipeline.
    
    This state is passed between nodes and tracks the complete lifecycle
    of content from initial fetching through final storage.
    """
    # Source identification
    source_type: Literal["youtube", "reddit"]
    source_url: str
    content_id: Optional[str]  # YouTube video ID or Reddit post ID
    
    # Content storage
    raw_content: Optional[str]  # Raw transcript or post content
    processed_content: Optional[str]  # Cleaned/formatted content
    summary: Optional[str]  # AI-generated summary
    embeddings: Optional[List[float]]  # Vector embeddings
    relevance_score: Optional[float]  # Content relevance score (0.0-1.0)
    
    # Processing state
    status: Literal["pending", "processing", "completed", "failed"]
    current_node: Optional[str]  # Current processing node
    error_message: Optional[str]
    retry_count: int
    
    # Metadata storage
    metadata: Dict[str, Any]  # Flexible metadata storage
    
    # Timestamps
    created_at: Optional[str]  # ISO format timestamp
    updated_at: Optional[str]  # ISO format timestamp
    completed_at: Optional[str]  # ISO format timestamp


class YouTubeMetadata(TypedDict):
    """Metadata structure for YouTube content."""
    video_id: str
    title: Optional[str]
    duration: Optional[float]  # Duration in seconds
    transcript_method: Literal["api", "whisper"]  # How transcript was obtained
    whisper_model: Optional[str]  # If using Whisper transcription
    language: Optional[str]
    channel: Optional[str]
    upload_date: Optional[str]


class RedditMetadata(TypedDict):
    """Metadata structure for Reddit content."""
    post_id: str
    subreddit: str
    title: str
    author: str
    score: int
    num_comments: int
    created_utc: float
    permalink: str
    is_self: bool
    link_flair_text: Optional[str]
    included_comments: int  # Number of comments included in content
    sort_type: str  # How posts were sorted when fetched
    time_filter: str  # Time filter used when fetching


class ProcessingConfig(TypedDict):
    """Configuration for processing pipeline."""
    # Content fetching
    youtube_whisper_model: str
    reddit_comment_limit: int
    reddit_include_comments: bool
    
    # Summarization
    summarization_model: str
    max_summary_length: int
    summary_style: Literal["brief", "detailed", "bullet_points"]
    
    # Embeddings
    embedding_model: str
    embedding_dimensions: int
    
    # Error handling
    max_retries: int
    retry_delay: float  # Seconds between retries
    timeout: float  # Request timeout in seconds


class BatchProcessingState(TypedDict):
    """State for batch processing multiple content items."""
    batch_id: str
    total_items: int
    processed_items: int
    failed_items: int
    status: Literal["pending", "processing", "completed", "failed"]
    items: List[ContentState]
    config: ProcessingConfig
    created_at: str
    updated_at: str


# Type aliases for better readability
ContentMetadata = Union[YouTubeMetadata, RedditMetadata]
ProcessingStatus = Literal["pending", "processing", "completed", "failed"]
SourceType = Literal["youtube", "reddit"]


def create_content_state(
    source_type: SourceType,
    source_url: str,
    content_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> ContentState:
    """Factory function to create a new ContentState with defaults.
    
    Args:
        source_type: Type of content source
        source_url: URL of the content
        content_id: Optional content ID (video ID, post ID)
        metadata: Optional metadata dict
        
    Returns:
        ContentState with initialized defaults
    """
    now = datetime.now(timezone.utc).isoformat()
    
    return ContentState(
        source_type=source_type,
        source_url=source_url,
        content_id=content_id,
        raw_content=None,
        processed_content=None,
        summary=None,
        embeddings=None,
        relevance_score=None,
        status="pending",
        current_node=None,
        error_message=None,
        retry_count=0,
        metadata=metadata or {},
        created_at=now,
        updated_at=now,
        completed_at=None
    )


def update_state_status(
    state: ContentState,
    status: ProcessingStatus,
    current_node: Optional[str] = None,
    error_message: Optional[str] = None
) -> ContentState:
    """Helper function to update state status and timestamps.
    
    Args:
        state: Current state to update
        status: New processing status
        current_node: Current processing node name
        error_message: Error message if status is 'failed'
        
    Returns:
        Updated ContentState
    """
    now = datetime.now(timezone.utc).isoformat()
    
    # Create a copy to avoid mutation
    updated_state = state.copy()
    updated_state["status"] = status
    updated_state["updated_at"] = now
    
    if current_node is not None:
        updated_state["current_node"] = current_node
        
    if error_message is not None:
        updated_state["error_message"] = error_message
        
    if status == "completed":
        updated_state["completed_at"] = now
        
    return updated_state


def increment_retry_count(state: ContentState) -> ContentState:
    """Helper function to increment retry count.
    
    Args:
        state: Current state to update
        
    Returns:
        Updated ContentState with incremented retry count
    """
    updated_state = state.copy()
    updated_state["retry_count"] = state["retry_count"] + 1
    updated_state["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    return updated_state 