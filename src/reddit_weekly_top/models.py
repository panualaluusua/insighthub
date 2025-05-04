"""Data models for Reddit posts and related entities."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RedditPost(BaseModel):
    """Represents a Reddit post with essential information.
    
    Attributes:
        title: The title of the post.
        url: The URL of the post.
        score: The score (upvotes - downvotes) of the post.
        created_utc: The UTC timestamp when the post was created.
        author: The username of the post author.
        is_promoted: Whether the post is promoted content.
        subreddit: The subreddit where the post was made.
        permalink: The Reddit permalink to the post.
        thumbnail: URL to the post thumbnail, if available.
        selftext: The text content of self (text-only) posts.
    """

    title: str = Field(..., description="The title of the post")
    url: str = Field(..., description="The URL of the post")
    score: int = Field(..., description="The score (upvotes - downvotes) of the post")
    created_utc: datetime = Field(..., description="The UTC timestamp when the post was created")
    author: str = Field(..., description="The username of the post author")
    is_promoted: bool = Field(default=False, description="Whether the post is promoted content")
    subreddit: str = Field(..., description="The subreddit where the post was made")
    permalink: str = Field(..., description="The Reddit permalink to the post")
    thumbnail: Optional[str] = Field(None, description="URL to the post thumbnail, if available")
    selftext: str = Field(default="", description="The text content of self (text-only) posts") 