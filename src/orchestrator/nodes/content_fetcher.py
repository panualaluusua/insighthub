"""ContentFetcherNode implementation for LangGraph orchestrator.

This node routes content fetching to the appropriate processor
(YouTube or Reddit) based on the source_type in the ContentState.
"""

import re
from typing import Optional
from datetime import datetime, timezone

from langsmith import traceable

from ..state import ContentState, update_state_status, YouTubeMetadata, RedditMetadata
from ...youtube_processor import YouTubeProcessor
from ...reddit_processor import RedditProcessor


class ContentFetcherNode:
    """Node for routing content fetching to appropriate processors.
    
    This node examines the source_type in ContentState and routes
    the request to either YouTubeProcessor or RedditProcessor.
    It updates the state with fetched content, metadata, and status.
    """

    def __init__(self):
        """Initialize the ContentFetcherNode."""
        self._youtube_processor: Optional[YouTubeProcessor] = None
        self._reddit_processor: Optional[RedditProcessor] = None

    @property
    def youtube_processor(self) -> YouTubeProcessor:
        """Lazy initialization of YouTubeProcessor."""
        if self._youtube_processor is None:
            self._youtube_processor = YouTubeProcessor()
        return self._youtube_processor

    @property
    def reddit_processor(self) -> RedditProcessor:
        """Lazy initialization of RedditProcessor."""
        if self._reddit_processor is None:
            self._reddit_processor = RedditProcessor()
        return self._reddit_processor

    @traceable(name="content_fetcher")
    def __call__(self, state: ContentState) -> ContentState:
        """Process content fetching based on source type.
        
        Args:
            state: Current ContentState with source_type and source_url
            
        Returns:
            Updated ContentState with fetched content or error information
        """
        try:
            # Update state to indicate processing has started
            updated_state = update_state_status(
                state, 
                status="processing", 
                current_node="content_fetcher"
            )

            source_type = state["source_type"]
            source_url = state["source_url"]

            if source_type == "youtube":
                return self._process_youtube_content(updated_state, source_url)
            elif source_type == "reddit":
                return self._process_reddit_content(updated_state, source_url)
            else:
                # Handle invalid source type
                return update_state_status(
                    updated_state,
                    status="failed",
                    current_node="content_fetcher",
                    error_message=f"Unsupported source type: {source_type}"
                )

        except Exception as e:
            # Catch any unexpected errors
            return update_state_status(
                state,
                status="failed",
                current_node="content_fetcher",
                error_message=f"Unexpected error in ContentFetcherNode: {str(e)}"
            )

    @traceable(name="youtube_content_processing")
    def _process_youtube_content(self, state: ContentState, url: str) -> ContentState:
        """Process YouTube content using YouTubeProcessor.
        
        Args:
            state: Current ContentState
            url: YouTube URL to process
            
        Returns:
            Updated ContentState with YouTube content and metadata
        """
        try:
            # Extract video ID
            video_id = self.youtube_processor.get_video_id(url)
            if not video_id:
                return update_state_status(
                    state,
                    status="failed",
                    error_message=f"Could not extract video ID from URL: {url}"
                )

            # Get transcript using base model (as specified in tests)
            transcript = self.youtube_processor.get_transcript(url, model_size="base")

            # Create YouTube metadata
            youtube_metadata: YouTubeMetadata = {
                "video_id": video_id,
                "title": None,  # Could be enhanced to fetch title from API
                "duration": None,  # Could be enhanced to fetch duration
                "transcript_method": "whisper",
                "whisper_model": "base",
                "language": None,  # Could be enhanced to detect language
                "channel": None,  # Could be enhanced to fetch channel info
                "upload_date": None  # Could be enhanced to fetch upload date
            }

            # Update state with fetched content
            result_state = state.copy()
            result_state["raw_content"] = transcript
            result_state["content_id"] = video_id
            result_state["metadata"] = {**state["metadata"], **youtube_metadata}
            result_state["updated_at"] = datetime.now(timezone.utc).isoformat()

            return result_state

        except ValueError as e:
            # Handle YouTubeProcessor errors
            return update_state_status(
                state,
                status="failed",
                error_message=str(e)
            )
        except Exception as e:
            # Handle unexpected errors
            return update_state_status(
                state,
                status="failed",
                error_message=f"Failed to process YouTube content: {str(e)}"
            )

    @traceable(name="reddit_content_processing")
    def _process_reddit_content(self, state: ContentState, url: str) -> ContentState:
        """Process Reddit content using RedditProcessor.
        
        Args:
            state: Current ContentState
            url: Reddit URL to process
            
        Returns:
            Updated ContentState with Reddit content and metadata
        """
        try:
            # Extract post ID from URL
            post_id = self._extract_reddit_post_id(url)
            
            # Extract subreddit from URL
            subreddit = self._extract_subreddit_from_url(url)
            if not subreddit:
                return update_state_status(
                    state,
                    status="failed",
                    error_message=f"Could not extract subreddit from URL: {url}"
                )

            # Fetch the specific post (we get posts from subreddit and find our post)
            posts = self.reddit_processor.fetch_posts(
                subreddit_name=subreddit,
                limit=50,  # Fetch more posts to find the specific one
                sort_type="new"  # Use 'new' to get recent posts which might include our target
            )

            # Find the specific post if we have a post_id
            target_post = None
            if post_id:
                target_post = next((post for post in posts if post.id == post_id), None)
            
            # If we can't find the specific post, use the first post as fallback
            if not target_post and posts:
                target_post = posts[0]
                post_id = target_post.id

            if not target_post:
                return update_state_status(
                    state,
                    status="failed",
                    error_message=f"Could not fetch Reddit post from {url}"
                )

            # Process the post content
            processed_content = self.reddit_processor.process_post_content(
                target_post,
                include_comments=True,
                comment_limit=5
            )

            # Create Reddit metadata
            reddit_metadata: RedditMetadata = {
                "post_id": target_post.id,
                "subreddit": target_post.subreddit,
                "title": target_post.title,
                "author": target_post.author,
                "score": target_post.score,
                "num_comments": target_post.num_comments,
                "created_utc": target_post.created_utc,
                "permalink": target_post.permalink,
                "is_self": target_post.is_self,
                "link_flair_text": target_post.link_flair_text,
                "included_comments": 5,  # Number of comments we included
                "sort_type": "new",  # How we sorted when fetching
                "time_filter": "all"  # Time filter used
            }

            # Update state with fetched content
            result_state = state.copy()
            result_state["raw_content"] = processed_content
            result_state["content_id"] = target_post.id
            result_state["metadata"] = {**state["metadata"], **reddit_metadata}
            result_state["updated_at"] = datetime.now(timezone.utc).isoformat()

            return result_state

        except ValueError as e:
            # Handle RedditProcessor errors
            return update_state_status(
                state,
                status="failed",
                error_message=str(e)
            )
        except Exception as e:
            # Handle unexpected errors
            return update_state_status(
                state,
                status="failed",
                error_message=f"Failed to process Reddit content: {str(e)}"
            )

    def _extract_reddit_post_id(self, url: str) -> Optional[str]:
        """Extract Reddit post ID from URL.
        
        Args:
            url: Reddit URL
            
        Returns:
            Post ID if found, None otherwise
        """
        # Reddit URL pattern: /r/subreddit/comments/post_id/title/
        patterns = [
            r'/r/[^/]+/comments/([a-zA-Z0-9]+)/',
            r'/comments/([a-zA-Z0-9]+)/'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None

    def _extract_subreddit_from_url(self, url: str) -> Optional[str]:
        """Extract subreddit name from URL.
        
        Args:
            url: Reddit URL
            
        Returns:
            Subreddit name if found, None otherwise
        """
        # Reddit URL pattern: /r/subreddit/...
        pattern = r'/r/([^/]+)/'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        
        return None 