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

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status() 

            posts = []
            response_json = response.json() 

            if not isinstance(response_json, dict) or "data" not in response_json or not isinstance(response_json["data"], dict) or "children" not in response_json["data"] or not isinstance(response_json["data"]["children"], list):
                logger.warning(f"Unexpected API response structure for r/{subreddit}. Expected 'data' with 'children' list. Got: {response_json}")
                return []

            for child in response_json["data"]["children"]:
                if not isinstance(child, dict) or "data" not in child or not isinstance(child["data"], dict):
                    logger.warning(f"Skipping post due to unexpected structure: {child}")
                    continue

                post_data = child["data"]
                
                # Extract data with robust fallbacks for all fields expected by RedditPost
                title_val = post_data.get("title", "N/A")
                url_val = post_data.get("url", "")
                score_val = post_data.get("score", 0)
                author_val = post_data.get("author", "N/A")
                created_utc_val = post_data.get("created_utc", 0)
                
                # Ensure subreddit_name is derived correctly
                subreddit_api_val = post_data.get("subreddit")
                subreddit_val = subreddit_api_val if subreddit_api_val is not None else subreddit # Fallback to function arg
                if subreddit_val is None: subreddit_val = "N/A" # Ultimate fallback

                permalink_api_val = post_data.get("permalink")
                # Ensure permalink is a full URL or an empty string if not available
                permalink_val = f"https://www.reddit.com{permalink_api_val}" if permalink_api_val else ""

                selftext_val = post_data.get("selftext", "")
                num_comments_val = post_data.get("num_comments", 0)
                thumbnail_val = post_data.get("thumbnail")

                # Clean up thumbnail URL
                if thumbnail_val == "self" or thumbnail_val == "default" or not thumbnail_val or not thumbnail_val.startswith("http"):
                    thumbnail_val = None
                
                # Convert timestamp to datetime object
                try:
                    created_dt = datetime.fromtimestamp(float(created_utc_val if created_utc_val is not None else 0))
                except (TypeError, ValueError):
                    created_dt = datetime.fromtimestamp(0) # Default to epoch

                # Construct the dictionary for Pydantic model instantiation
                post_args = {
                    "title": title_val,
                    "url": url_val,
                    "score": int(score_val), # Ensure int
                    "author": author_val,
                    "created_utc": created_dt,
                    "subreddit": subreddit_val,
                    "permalink": permalink_val,
                    "selftext": selftext_val,
                    "num_comments": int(num_comments_val), # Ensure int
                    "thumbnail": thumbnail_val
                    # is_promoted will use the model's default value (False)
                }
                
                try:
                    post_instance = RedditPost(**post_args)
                    posts.append(post_instance)
                except Exception as e_pydantic:
                    # Log the exact data that caused the Pydantic error
                    logger.error(f"Pydantic validation failed for data: {post_args}. Error: {e_pydantic}")
                    # Re-raise the error to be caught by the outer try-except if needed
                    raise e_pydantic # Changed to re-raise the specific Pydantic error

            return posts
        except RequestException as e_req: # Specific exception for requests issues
            logger.error(f"Failed to fetch posts from r/{subreddit}: {e_req}")
            raise
        # Removed KeyError catch as .get() with defaults should prevent most KeyErrors from post_data
        except Exception as e_general: 
            # This will catch the re-raised Pydantic error or other unexpected errors
            logger.error(f"An unexpected error occurred while fetching posts from r/{subreddit}: {e_general}. Response: {response.text[:500] if 'response' in locals() and hasattr(response, 'text') else 'N/A'}")
            raise RequestException(f"Unexpected error for r/{subreddit}: {e_general}") from e_general

    def close_session(self) -> None:
        """Close the requests session."""
        if self.session:
            self.session.close()
            logger.info("RedditClient session closed.")