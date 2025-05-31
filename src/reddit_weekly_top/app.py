"""Main application entry point for InsightHub."""

import streamlit as st
from typing import List, Dict
import sys
import os

# Add the project root to Python path
print(f"DEBUG: __file__ = {__file__}")
print(f"DEBUG: os.path.abspath(__file__) = {os.path.abspath(__file__)}")
print(f"DEBUG: CWD before sys.path manipulation = {os.getcwd()}")
print(f"DEBUG: sys.path before modification = {sys.path}")
project_root_for_sys_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"DEBUG: Inserting into sys.path at index 0: {project_root_for_sys_path}")
sys.path.insert(0, project_root_for_sys_path)
print(f"DEBUG: sys.path after modification = {sys.path}")
print(f"DEBUG: CWD after sys.path manipulation = {os.getcwd()}")

from reddit_weekly_top.reddit_client import RedditClient
print("DEBUG: Successfully imported RedditClient")
from reddit_weekly_top.youtube_client import YouTubeClient
from reddit_weekly_top.constants import SUBREDDIT_CATEGORIES, DEFAULT_PODCAST_PROMPTS
from reddit_weekly_top.utils import initialize_session_state

@st.cache_resource
def get_reddit_client() -> RedditClient:
    """Create or get a cached Reddit client instance."""
    return RedditClient(user_agent="InsightHub/1.0")

@st.cache_resource
def get_youtube_client() -> YouTubeClient:
    """Create or get a cached YouTube client instance."""
    return YouTubeClient()

def main():
    """Main application function."""
    st.set_page_config(layout="wide")
    st.title("InsightHub: Reddit & YouTube Aggregator")
    st.markdown("Fetch and list URLs from your favorite subreddits and YouTube channels.")

    # Initialize session state
    initialize_session_state()

    # Sidebar for configuration
    with st.sidebar:
        st.header("Reddit Category Selection")
        category_options = list(SUBREDDIT_CATEGORIES.keys())
        if "All" in category_options:
            category_options.remove("All")
        selected_category = st.selectbox(
            "Select subreddit category:",
            options=category_options,
            key="sidebar_category_selectbox"
        )
        time_window = st.selectbox(
            "Reddit time window:",
            options=["week", "month"],
            index=0,
            key="reddit_time_window_selectbox"
        )
        num_posts = st.number_input(
            "Number of posts per subreddit:",
            min_value=1,
            max_value=50,
            value=10,
            key="reddit_num_posts_input"
        )
        fetch_reddit = st.button(
            "Fetch Reddit Posts",
            key="fetch_reddit_posts_button",
            use_container_width=True
        )
        st.markdown("---")
        st.header("Default Prompt Selector")
        DEFAULT_PROMPTS = DEFAULT_PODCAST_PROMPTS
        selected_prompt = st.selectbox(
            "Choose a default prompt:",
            options=DEFAULT_PROMPTS,
            key="default_prompt_selectbox"
        )
        st.markdown("**Selected Prompt:**")
        st.text_area("", value=selected_prompt, height=120, key="selected_prompt_text", disabled=True)

    # Main content
    st.header("Reddit Posts")
    if 'reddit_fetched_posts' not in st.session_state:
        st.session_state.reddit_fetched_posts = []
    
    if fetch_reddit:
        reddit_client = get_reddit_client()
        subreddits = SUBREDDIT_CATEGORIES[selected_category]
        all_posts = []
        for subreddit in subreddits:
            try:
                posts = reddit_client.get_top_weekly_posts(subreddit, limit=num_posts) if time_window == "week" \
                    else reddit_client.get_top_monthly_posts(subreddit, limit=num_posts)
                all_posts.extend(posts)
            except Exception as e:
                st.warning(f"Error fetching from r/{subreddit}: {str(e)}")
        # Sort all posts by score, descending
        all_posts_sorted = sorted(all_posts, key=lambda post: getattr(post, 'score', 0), reverse=True)
        # Display only the top N posts overall
        st.session_state.reddit_fetched_posts = all_posts_sorted[:num_posts]
    
    # Display fetched posts
    if st.session_state.reddit_fetched_posts:
        for post in st.session_state.reddit_fetched_posts:
            st.markdown(f"- [{post.title}]({post.url}) (Score: {post.score})")

        # --- URL listing and copy functionality ---
        st.subheader("Reddit Post URLs")
        reddit_urls = "\n".join([post.url for post in st.session_state.reddit_fetched_posts])
        st.text_area("Fetched Reddit URLs:", value=reddit_urls, height=120, key="reddit_urls_textarea")
        if st.button("📋 Copy Reddit URLs", key="copy_reddit_urls_button", use_container_width=True):
            st.session_state.copied_text = reddit_urls
            st.success("Reddit URLs copied! (Use Ctrl+C to copy from the text area if needed)")
    else:
        st.info("No Reddit posts to display. Use the sidebar to fetch posts.")

    st.header("YouTube Videos")
    if not os.getenv("YOUTUBE_API"):
        st.warning("YouTube API key not set. Set YOUTUBE_API in your .env file.")
    else:
        DEFAULT_YOUTUBE_CHANNEL_NAMES = "AI Jason,David Ondrej,Zen van Riel"
        youtube_channel_names_str = st.text_input(
            "YouTube Channel Names (comma-separated):",
            value=DEFAULT_YOUTUBE_CHANNEL_NAMES,
            key="youtube_channel_names_input"
        )
        youtube_num_videos = st.number_input(
            "Number of videos per channel:",
            min_value=1,
            max_value=20,
            value=5,
            key="youtube_num_videos_input"
        )
        if st.button("Fetch YouTube Videos", key="fetch_youtube_videos_button", use_container_width=True):
            if not youtube_channel_names_str:
                st.warning("Please enter at least one YouTube Channel Name.")
                st.session_state.youtube_videos = []
            else:
                channel_names = [name.strip() for name in youtube_channel_names_str.split(',') if name.strip()]
                try:
                    youtube_client = get_youtube_client()
                    st.session_state.youtube_videos = youtube_client.fetch_videos_from_channels(
                        channel_names,
                        youtube_num_videos
                    )
                except Exception as e:
                    st.warning(f"Error fetching YouTube videos: {str(e)}")
                    st.session_state.youtube_videos = []

        # Display fetched YouTube videos (list view)
        if st.session_state.youtube_videos:
            st.subheader("YouTube Video List")
            for video in st.session_state.youtube_videos:
                st.markdown(f"- [{video['title']}]({video['url']}) ({video['channel_title']})")

            # --- URL listing and copy functionality ---
            st.subheader("YouTube Video URLs")
            youtube_urls = "\n".join([video['url'] for video in st.session_state.youtube_videos])
            st.text_area("Fetched YouTube URLs:", value=youtube_urls, height=120, key="youtube_urls_textarea")
            if st.button("📋 Copy YouTube URLs", key="copy_youtube_urls_button", use_container_width=True):
                st.session_state.youtube_copied_text = youtube_urls
                st.success("YouTube URLs copied! (Use Ctrl+C to copy from the text area if needed)")
        else:
            st.info("No YouTube videos to display. Use the sidebar to fetch videos.")

if __name__ == "__main__":
    main()
