#!/usr/bin/env python3
"""
Test script for Reddit processor functionality.
Usage: python run_reddit_test.py [subreddit_name]
Example: python run_reddit_test.py programming
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from reddit_processor import RedditProcessor


def main():
    """Test the Reddit processor with a specific subreddit."""
    if len(sys.argv) < 2:
        subreddit_name = "programming"  # Default test subreddit
        print(f"No subreddit specified, using default: r/{subreddit_name}")
    else:
        subreddit_name = sys.argv[1]
    
    print(f"Testing Reddit processor with r/{subreddit_name}...")
    
    try:
        # Initialize the processor
        processor = RedditProcessor()
        print("✅ Reddit processor initialized successfully")
        
        # Validate the subreddit
        if not processor.validate_subreddit(subreddit_name):
            print(f"❌ Subreddit r/{subreddit_name} is not accessible")
            return
        
        print(f"✅ Subreddit r/{subreddit_name} is valid and accessible")
        
        # Fetch some posts
        print("Fetching top 5 posts...")
        posts = processor.fetch_posts(
            subreddit_name=subreddit_name,
            limit=5,
            sort_type="hot"
        )
        
        print(f"✅ Successfully fetched {len(posts)} posts")
        
        # Process and display the first post
        if posts:
            print("\n" + "="*80)
            print("SAMPLE POST PROCESSING:")
            print("="*80)
            
            first_post = posts[0]
            processed_content = processor.process_post_content(
                first_post, 
                include_comments=True, 
                comment_limit=3
            )
            
            print(f"Post ID: {first_post.id}")
            print(f"URL: https://reddit.com{first_post.permalink}")
            print("\nProcessed Content:")
            print("-" * 40)
            print(processed_content)
            
            # Get full content summary
            print("\n" + "="*80)
            print("CONTENT SUMMARY:")
            print("="*80)
            
            summary = processor.get_content_summary(
                subreddit_name=subreddit_name,
                limit=3,
                sort_type="hot"
            )
            
            print(f"Subreddit: r/{summary['subreddit']}")
            print(f"Total posts: {summary['total_posts']}")
            print(f"Timestamp: {summary['timestamp']}")
            
            print("\nPost Titles:")
            for item in summary['processed_content']:
                print(f"- {item['title']} (Score: {item['score']})")
        
        print("\n✅ Reddit processor test completed successfully!")
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nTo fix this, you need to:")
        print("1. Create a Reddit app at https://www.reddit.com/prefs/apps")
        print("2. Set the following environment variables:")
        print("   - REDDIT_CLIENT_ID=your_client_id")
        print("   - REDDIT_SECRET=your_client_secret")
        print("   - REDDIT_USER_AGENT=your_app_name/1.0")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 