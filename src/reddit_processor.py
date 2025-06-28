import praw
import os
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime, timezone


class RedditPost(BaseModel):
    """Data model for a Reddit post."""
    id: str
    title: str
    selftext: str
    url: str
    score: int
    num_comments: int
    created_utc: float
    subreddit: str
    author: str
    permalink: str
    is_self: bool
    link_flair_text: Optional[str] = None


class RedditComment(BaseModel):
    """Data model for a Reddit comment."""
    id: str
    body: str
    score: int
    created_utc: float
    author: str
    is_submitter: bool


class RedditProcessor:
    """
    A class to process Reddit content by fetching posts from subreddits.
    """

    def __init__(self):
        """
        Initialize the Reddit processor with PRAW client.
        
        Requires environment variables:
        - REDDIT_CLIENT_ID
        - REDDIT_SECRET
        - REDDIT_USER_AGENT (optional, defaults to 'content-processor/1.0')
        """
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "content-processor/1.0")
        
        if not client_id or not client_secret:
            raise ValueError(
                "Reddit API credentials not found. Please set REDDIT_CLIENT_ID and REDDIT_SECRET environment variables."
            )
        
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def validate_subreddit(self, subreddit_name: str) -> bool:
        """
        Validates if a subreddit exists and is accessible.
        
        Args:
            subreddit_name: Name of the subreddit (without 'r/' prefix)
            
        Returns:
            True if subreddit is valid and accessible, False otherwise
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            # Try to access the subreddit display name to check if it exists
            _ = subreddit.display_name
            return True
        except Exception:
            return False

    def fetch_posts(
        self,
        subreddit_name: str,
        limit: int = 10,
        time_filter: str = "day",
        sort_type: str = "hot"
    ) -> List[RedditPost]:
        """
        Fetches posts from a specified subreddit.
        
        Args:
            subreddit_name: Name of the subreddit (without 'r/' prefix)
            limit: Maximum number of posts to fetch (default: 10)
            time_filter: Time filter for posts ('hour', 'day', 'week', 'month', 'year', 'all')
            sort_type: How to sort posts ('hot', 'new', 'top', 'rising')
            
        Returns:
            List of RedditPost objects
            
        Raises:
            ValueError: If subreddit is invalid or inaccessible
        """
        if not self.validate_subreddit(subreddit_name):
            raise ValueError(f"Subreddit '{subreddit_name}' is invalid or inaccessible")
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            # Get posts based on sort type
            if sort_type == "hot":
                submissions = subreddit.hot(limit=limit)
            elif sort_type == "new":
                submissions = subreddit.new(limit=limit)
            elif sort_type == "top":
                submissions = subreddit.top(time_filter=time_filter, limit=limit)
            elif sort_type == "rising":
                submissions = subreddit.rising(limit=limit)
            else:
                raise ValueError(f"Invalid sort_type: {sort_type}")
            
            for submission in submissions:
                post = RedditPost(
                    id=submission.id,
                    title=submission.title,
                    selftext=submission.selftext,
                    url=submission.url,
                    score=submission.score,
                    num_comments=submission.num_comments,
                    created_utc=submission.created_utc,
                    subreddit=submission.subreddit.display_name,
                    author=str(submission.author) if submission.author else "[deleted]",
                    permalink=submission.permalink,
                    is_self=submission.is_self,
                    link_flair_text=submission.link_flair_text
                )
                posts.append(post)
            
            return posts
            
        except Exception as e:
            raise ValueError(f"Failed to fetch posts from r/{subreddit_name}: {e}")

    def fetch_comments(self, post_id: str, limit: int = 5) -> List[RedditComment]:
        """
        Fetches top comments from a specific post.
        
        Args:
            post_id: Reddit post ID
            limit: Maximum number of top-level comments to fetch
            
        Returns:
            List of RedditComment objects
            
        Raises:
            ValueError: If post is invalid or inaccessible
        """
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # Remove "more comments" objects
            
            comments = []
            for comment in submission.comments[:limit]:
                if hasattr(comment, 'body') and comment.body != '[deleted]':
                    reddit_comment = RedditComment(
                        id=comment.id,
                        body=comment.body,
                        score=comment.score,
                        created_utc=comment.created_utc,
                        author=str(comment.author) if comment.author else "[deleted]",
                        is_submitter=comment.is_submitter
                    )
                    comments.append(reddit_comment)
            
            return comments
            
        except Exception as e:
            raise ValueError(f"Failed to fetch comments for post {post_id}: {e}")

    def process_post_content(self, post: RedditPost, include_comments: bool = True, comment_limit: int = 5) -> str:
        """
        Processes a Reddit post into a cleaned text format suitable for analysis.
        
        Args:
            post: RedditPost object to process
            include_comments: Whether to include top comments in the output
            comment_limit: Maximum number of comments to include
            
        Returns:
            Cleaned and formatted text content
        """
        content_parts = []
        
        # Add post title
        content_parts.append(f"Title: {post.title}")
        
        # Add post content if it's a text post
        if post.is_self and post.selftext.strip():
            content_parts.append(f"Content: {post.selftext}")
        elif not post.is_self:
            content_parts.append(f"Link: {post.url}")
        
        # Add metadata
        content_parts.append(f"Score: {post.score}")
        content_parts.append(f"Comments: {post.num_comments}")
        content_parts.append(f"Subreddit: r/{post.subreddit}")
        
        if post.link_flair_text:
            content_parts.append(f"Flair: {post.link_flair_text}")
        
        # Add top comments if requested
        if include_comments and post.num_comments > 0:
            try:
                comments = self.fetch_comments(post.id, limit=comment_limit)
                if comments:
                    content_parts.append("\nTop Comments:")
                    for i, comment in enumerate(comments, 1):
                        content_parts.append(f"{i}. [{comment.score} points] {comment.body[:500]}{'...' if len(comment.body) > 500 else ''}")
            except Exception:
                # If we can't fetch comments, just continue without them
                pass
        
        return "\n".join(content_parts)

    def get_content_summary(self, subreddit_name: str, **kwargs) -> Dict[str, Any]:
        """
        Fetches and processes content from a subreddit into a summary format.
        
        Args:
            subreddit_name: Name of the subreddit
            **kwargs: Additional parameters for fetch_posts
            
        Returns:
            Dictionary containing processed content and metadata
        """
        posts = self.fetch_posts(subreddit_name, **kwargs)
        
        processed_content = []
        for post in posts:
            content = self.process_post_content(post)
            processed_content.append({
                "post_id": post.id,
                "title": post.title,
                "content": content,
                "score": post.score,
                "url": f"https://reddit.com{post.permalink}",
                "created_utc": post.created_utc
            })
        
        return {
            "subreddit": subreddit_name,
            "total_posts": len(posts),
            "processed_content": processed_content,
            "timestamp": datetime.now(timezone.utc).isoformat()
        } 