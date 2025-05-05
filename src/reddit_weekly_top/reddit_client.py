"""Reddit API client for fetching top weekly posts."""

import logging
from datetime import datetime
from typing import List

import requests  # Keep this import
from requests.exceptions import RequestException

from reddit_weekly_top.models import RedditPost

logger = logging.getLogger(__name__)

class RedditClient:
    """Client for interacting with Reddit's API.
    
    Attributes:
        user_agent: Custom user agent string for API requests.
        base_url: Base URL for Reddit's API.
        session: requests.Session object for making HTTP requests.
    """

    def __init__(self, user_agent: str) -> None:
        """Initialize the Reddit client.
        
        Args:
            user_agent: Custom user agent string for API requests.
        """
        self.user_agent = user_agent
        self.base_url = "https://www.reddit.com"
        self.session = requests.Session()  # Initialize the session
        self.session.headers.update({"User-Agent": self.user_agent}) # Set User-Agent for the session

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
        # Headers are now set on the session, no need to pass them here unless overriding
        # headers = {"User-Agent": self.user_agent} # Remove this line

        try:
            # Use self.session.get instead of requests.get
            response = self.session.get(url, params=params) # Removed headers argument
            response.raise_for_status() # This will raise HTTPError for bad responses (4xx or 5xx)

            posts = []
            response_json = response.json() # Parse JSON once

            # Add checks for expected structure before accessing keys
            if not isinstance(response_json, dict) or "data" not in response_json or not isinstance(response_json["data"], dict) or "children" not in response_json["data"] or not isinstance(response_json["data"]["children"], list):
                logger.warning(f"Unexpected API response structure for r/{subreddit}. Expected 'data' with 'children' list. Got: {response_json}")
                return [] # Return empty list for malformed response

            for child in response_json["data"]["children"]:
                # Ensure child and child['data'] are dictionaries before accessing keys
                if not isinstance(child, dict) or "data" not in child or not isinstance(child["data"], dict):
                    logger.warning(f"Skipping malformed child item in response for r/{subreddit}: {child}")
                    continue

                post_data = child["data"]
                
                # Filter promoted posts directly here
                if post_data.get("promoted", False):
                    continue
                
                # Basic check for essential keys before creating RedditPost
                required_keys = ["title", "permalink", "score", "created_utc", "author", "subreddit"]
                if not all(key in post_data for key in required_keys):
                    logger.warning(f"Skipping post item with missing essential keys in response for r/{subreddit}: {post_data.get('permalink', 'N/A')}")
                    continue

                # Create full Reddit URL from permalink
                full_reddit_url = f"https://www.reddit.com{post_data['permalink']}"
                posts.append(
                    RedditPost(
                        title=post_data["title"],
                        url=full_reddit_url,
                        score=post_data["score"],
                        created_utc=datetime.fromtimestamp(post_data["created_utc"]),
                        author=post_data["author"],
                        is_promoted=False, # Already filtered, so set to False
                        subreddit=post_data["subreddit"],
                        permalink=post_data["permalink"],
                        thumbnail=post_data.get("thumbnail"),
                        selftext=post_data.get("selftext", "")
                    )
                )
            # Note: The number of posts returned might be less than 'limit'
            # if promoted posts were filtered out. The tests seem to account for this.
            return posts

        # RequestException includes ConnectionError, HTTPError, Timeout, TooManyRedirects
        # No need to catch HTTPError separately as raise_for_status() handles it.
        except RequestException as e:
            logger.error(f"Failed to fetch posts from r/{subreddit}: {e}")
            raise # Re-raise the original exception for tests/callers to handle
        except (KeyError, TypeError, ValueError) as e: # Catch potential JSON parsing or data access errors
             logger.error(f"Failed to parse API response from r/{subreddit}: {e} - Response text: {response.text if 'response' in locals() else 'N/A'}")
             # Return empty list on parsing error, as tests expect this for malformed data
             return []