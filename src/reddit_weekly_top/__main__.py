"""Main module for the Reddit Weekly Top application."""

import argparse
import logging
import sys
from typing import List, Optional

from reddit_weekly_top.config import config
from reddit_weekly_top.reddit_client import RedditClient

logger = logging.getLogger(__name__)

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.
    
    Args:
        args: List of command line arguments. Defaults to None.
        
    Returns:
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Fetch top weekly posts from selected subreddits"
    )
    parser.add_argument(
        "-s", "--subreddits",
        nargs="+",
        help="List of subreddits to fetch posts from"
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=config.posts_limit,
        help="Number of posts to fetch per subreddit"
    )
    parser.add_argument(
        "-u", "--user-agent",
        default=config.user_agent,
        help="Custom user agent string"
    )
    
    return parser.parse_args(args)

def main(args: Optional[List[str]] = None) -> None:
    """Main function to fetch and display Reddit posts.
    
    Args:
        args: Command line arguments. Defaults to None.
    """
    logging.basicConfig(level=logging.INFO)
    parsed_args = parse_args(args)
    
    try:
        client = RedditClient(user_agent=parsed_args.user_agent)
        subreddits = parsed_args.subreddits or config.default_subreddits
        
        for subreddit in subreddits:
            print(f"\nTop posts from r/{subreddit}:")
            print("-" * 80)
            
            try:
                posts = client.get_top_weekly_posts(subreddit, limit=parsed_args.limit)
                for post in posts:
                    # Only print the Reddit discussion URL
                    print(f"Title: {post.title}")
                    print(f"URL: {post.url}")
                    print()
            except Exception as e:
                logger.error(f"Failed to fetch posts from r/{subreddit}: {e}")
                continue
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to fetch posts: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 