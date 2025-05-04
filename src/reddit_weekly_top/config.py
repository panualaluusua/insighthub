"""Configuration management for the Reddit Weekly Top application."""

import os
from typing import List

from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config(BaseModel):
    """Application configuration settings.
    
    Attributes:
        user_agent: Custom user agent string for Reddit API requests.
        default_subreddits: List of default subreddits to fetch posts from.
        posts_limit: Number of posts to fetch per subreddit.
    """

    user_agent: str = os.getenv(
        "REDDIT_USER_AGENT",
        "Python:reddit-weekly-top:v0.1.0 (by /u/your_username)"
    )
    default_subreddits: List[str] = [
        "cursor",
        "ChatGPTCoding",
        "AI_Agents",
    ]
    posts_limit: int = int(os.getenv("REDDIT_POSTS_LIMIT", "13"))

# Create global config instance
config = Config() 