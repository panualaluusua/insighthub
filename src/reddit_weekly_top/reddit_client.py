"""Reddit API client for fetching top weekly posts."""

import logging
from datetime import datetime
from typing import List

import requests
from requests.exceptions import RequestException

from reddit_weekly_top.models import RedditPost

logger = logging.getLogger(__name__)

class RedditClient:
    """Client for interacting with Reddit's API.
    
    Attributes:
        user_agent: Custom user agent string for API requests.
        base_url: Base URL for Reddit's API.
    """

    def __init__(self, user_agent: str) -> None:
        """Initialize the Reddit client.
        
        Args:
            user_agent: Custom user agent string for API requests.
        """
        self.user_agent = user_agent
        self.base_url = "https://www.reddit.com"
        
    def get_top_weekly_posts(self, subreddit: str, limit: int = 10) -> List[RedditPost]:
        """Fetch top weekly posts from a subreddit.
        
        Args:
            subreddit: Name of the subreddit to fetch posts from.
            limit: Maximum number of posts to fetch. Defaults to 10.
            
        Returns:
            List of RedditPost objects.
            
        Raises:
            RequestException: If the API request fails.
        """
        return self._get_top_posts(subreddit, "week", limit)

    def get_top_monthly_posts(self, subreddit: str, limit: int = 10) -> List[RedditPost]:
        """Fetch top monthly posts from a subreddit.
        
        Args:
            subreddit: Name of the subreddit to fetch posts from.
            limit: Maximum number of posts to fetch. Defaults to 10.
            
        Returns:
            List of RedditPost objects.
            
        Raises:
            RequestException: If the API request fails.
        """
        return self._get_top_posts(subreddit, "month", limit)

    def _get_top_posts(self, subreddit: str, timeframe: str, limit: int) -> List[RedditPost]:
        """Internal method to fetch top posts from a subreddit for a given timeframe.
        
        Args:
            subreddit: Name of the subreddit to fetch posts from.
            timeframe: Time window for top posts (e.g., "week", "month").
            limit: Maximum number of posts to fetch.
            
        Returns:
            List of RedditPost objects.
            
        Raises:
            RequestException: If the API request fails.
        """
        url = f"{self.base_url}/r/{subreddit}/top.json"
        params = {
            "t": timeframe,
            "limit": limit
        }
        headers = {"User-Agent": self.user_agent}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            posts = []
            for child in response.json()["data"]["children"]:
                post_data = child["data"]
                # Create full Reddit URL from permalink
                full_reddit_url = f"https://www.reddit.com{post_data['permalink']}"
                posts.append(
                    RedditPost(
                        title=post_data["title"],
                        url=full_reddit_url,  # Use Reddit discussion URL instead of external URL
                        score=post_data["score"],
                        created_utc=datetime.fromtimestamp(post_data["created_utc"]),
                        author=post_data["author"],
                        is_promoted=post_data.get("promoted", False),
                        subreddit=post_data["subreddit"],
                        permalink=post_data["permalink"],
                        thumbnail=post_data.get("thumbnail"),
                        selftext=post_data.get("selftext", "")  # Add selftext field for text-only posts
                    )
                )
            return posts
            
        except RequestException as e:
            logger.error(f"Failed to fetch posts from r/{subreddit}: {e}")
            raise 