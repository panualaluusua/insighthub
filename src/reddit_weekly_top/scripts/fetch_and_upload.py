"""Script to fetch Reddit posts and upload them directly to NotebookLM."""

import argparse
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from dotenv import load_dotenv

from reddit_weekly_top.config import config
from reddit_weekly_top.models import RedditPost
from reddit_weekly_top.notebooklm.source_uploader import (
    NotebookLMSourceUploader,
    SourceUploaderConfig,
)
from reddit_weekly_top.reddit_client import RedditClient

logger = logging.getLogger(__name__)

def fetch_and_save_posts(
    subreddits: List[str],
    output_dir: Path,
    timeframe: str = "week",
    limit: int = 10,
    min_score: int = 0
) -> Path:
    """Fetch top posts from specified subreddits and save their URLs.
    
    Args:
        subreddits: List of subreddit names to fetch posts from.
        output_dir: Directory to save output files.
        timeframe: Time window for top posts ("week" or "month"). Defaults to "week".
        limit: Maximum number of posts to fetch per subreddit. Defaults to 10.
        min_score: Minimum score threshold for posts. Defaults to 0.
        
    Returns:
        Path to the URLs output file.
        
    Raises:
        Exception: If fetching or saving posts fails.
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize Reddit client
    client = RedditClient(user_agent=config.user_agent)
    
    # Fetch posts from all subreddits
    all_posts = []
    for subreddit in subreddits:
        try:
            if timeframe == "month":
                posts = client.get_top_monthly_posts(subreddit, limit=limit)
            else:
                posts = client.get_top_weekly_posts(subreddit, limit=limit)
            # Filter by minimum score
            filtered_posts = [post for post in posts if post.score >= min_score]
            all_posts.extend(filtered_posts)
            logger.info(
                f"Fetched {len(filtered_posts)} posts from r/{subreddit} "
                f"(min score: {min_score})"
            )
        except Exception as e:
            logger.error(f"Failed to fetch posts from r/{subreddit}: {e}")
            continue
    
    if not all_posts:
        raise Exception("No posts were fetched from any subreddit")
    
    # Sort posts by score
    all_posts.sort(key=lambda x: x.score, reverse=True)
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    urls_file = output_dir / f"reddit_urls_{timestamp}.txt"
    
    # Save URLs and print summary
    logger.info("\nFetched posts summary:")
    with open(urls_file, "w", encoding="utf-8") as f:
        for i, post in enumerate(all_posts, 1):
            f.write(f"{post.url}\n")
            logger.info(
                f"{i}. [r/{post.subreddit}] ({post.score} points) {post.title}"
            )
    
    logger.info(f"\nTotal posts saved: {len(all_posts)}")
    return urls_file

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.
    
    Args:
        args: List of command line arguments. Defaults to None.
        
    Returns:
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Fetch Reddit posts and upload them directly to NotebookLM"
    )
    
    # Reddit options
    parser.add_argument(
        "-s", "--subreddits",
        nargs="+",
        required=True,  # Make subreddits required since we don't need defaults
        help="List of subreddits to fetch posts from"
    )
    parser.add_argument(
        "-t", "--timeframe",
        choices=["week", "month"],
        default="week",
        help="Time window for top posts (week or month)"
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=10,
        help="Number of posts to fetch per subreddit"
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=0,
        help="Minimum score threshold for posts"
    )
    
    # NotebookLM options
    parser.add_argument(
        "--profile-dir",
        help="Chrome user profile directory"
    )
    parser.add_argument(
        "--upload-delay",
        type=float,
        default=2.0,
        help="Delay in seconds between URL uploads"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retries for failed uploads"
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=5.0,
        help="Delay in seconds between retries"
    )
    parser.add_argument(
        "--wait-timeout",
        type=int,
        default=10,
        help="Timeout for WebDriver wait operations"
    )
    
    return parser.parse_args(args)

def main(args: Optional[List[str]] = None) -> None:
    """Main function to fetch posts and upload them to NotebookLM.
    
    Args:
        args: Command line arguments. Defaults to None.
    """
    # Set up detailed logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s"  # Simplified format for better readability
    )
    
    # Reduce noise from selenium
    logging.getLogger('selenium').setLevel(logging.INFO)
    logging.getLogger('urllib3').setLevel(logging.INFO)
    
    # Load environment variables
    load_dotenv()
    
    parsed_args = parse_args(args)
    
    try:
        # Step 1: Fetch Reddit posts
        logger.info(f"Fetching {parsed_args.timeframe}ly posts from: {', '.join(parsed_args.subreddits)}")
        
        urls_file = fetch_and_save_posts(
            subreddits=parsed_args.subreddits,
            output_dir=Path("reddit_posts"),
            timeframe=parsed_args.timeframe,
            limit=parsed_args.limit,
            min_score=parsed_args.min_score
        )
        
        # Give user a chance to review the fetched posts
        logger.info(
            f"\nURLs have been saved to: {urls_file}"
            "\nPress Enter to continue with upload, or Ctrl+C to cancel..."
        )
        try:
            input()
        except KeyboardInterrupt:
            logger.info("Upload cancelled by user")
            sys.exit(0)
        
        # Step 2: Configure and run NotebookLM uploader
        config_kwargs = {
            "user_profile": parsed_args.profile_dir or os.getenv("CHROME_USER_PROFILE"),
            "upload_delay": parsed_args.upload_delay,
            "max_retries": parsed_args.max_retries,
            "retry_delay": parsed_args.retry_delay,
            "wait_timeout": parsed_args.wait_timeout,
            "keep_browser_open": True
        }
        
        try:
            uploader_config = SourceUploaderConfig.from_file(urls_file, **config_kwargs)
        except FileNotFoundError:
            logger.error(f"URL file not found: {urls_file}")
            sys.exit(1)
        
        uploader = NotebookLMSourceUploader(uploader_config)
        
        try:
            logger.info("Starting NotebookLM source upload automation")
            uploader.start()
            
            if uploader.verify_login_success():
                logger.info("Successfully logged in to NotebookLM")
                uploader.process_urls()
                logger.info("Source upload automation completed successfully")
            else:
                logger.error("Failed to verify login success")
                sys.exit(1)
            
        except KeyboardInterrupt:
            logger.info("Operation cancelled by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Source upload automation failed: {e}")
            sys.exit(1)
        finally:
            uploader.cleanup()
            
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 