"""Streamlit frontend for Reddit Weekly Top."""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from typing import List, Tuple
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import time

from reddit_weekly_top.reddit_client import RedditClient
from reddit_weekly_top.models import RedditPost

# --- Category Definitions ---
SUBREDDIT_CATEGORIES = {
    "AI / ML / Data": [
        "AI_Agents", "ChatGPT", "ChatGPTCoding", "ClaudeAI", "Codeium", "cursor", 
        "LangChain", "LLMDevs", "LocalLLaMA", "MachineLearning", "MLEngineering", 
        "ollama", "singularity", "datascience", "dataisbeautiful", "apachesark", 
        "databricks", "dataengineering", "analytics"
    ],
    "AI Coding (Specific)": [
        "AI_Agents", "ChatGPTCoding", "ClaudeAI", "Codeium", "cursor", "LangChain", 
        "LLMDevs", "LocalLLaMA", "MLEngineering", "ollama"
    ],
    "Software Dev / Tech": [
        "Python", "devops", "ExperiencedDevs", "ProgrammerHumor", "Workspaces", "n8n", "mcp"
    ],
    "Cycling / Outdoors": [
        "bicycletouring", "bicycling", "BicyclingCirclejerk", "bikepacking", "cycling", 
        "gravelcycling", "Justridingalong", "mountainbiking", "MTB", "randonneuring", 
        "trailrunning", "Ultralight", "Velo", "xcmtb", "xcountryskiing", "Zwift", 
        "bouldering", "HikerTrashMemes", "running", "RunningCirclejerk", "EarthPorn", 
        "landscaping"
    ],
    "Finance / Economics": [
        "Economics", "eupersonalfinance", "finance", "FinOps", "MiddleClassFinance", 
        "Omatalous", "wallstreetbets"
    ],
    "Gaming": [
        "Amd", "aoe4", "eu4", "XboxGamePass"
    ],
    "News / World": [
        "announcements", "europe", "worldnews", "UkraineWarVideoReport", "UkrainianConflict"
    ],
    "Finland Specific": [
        "arkisuomi", "Oulu", "Suomi"
    ],
    "Miscellaneous / Humor / Life": [
        "automation", "CameraObscura", "consulting", "daddit", "darknetdiaries", 
        "digitalminimalism", "DIY", "greentext", "instant_regret", "instantkarma", 
        "KidsAreFuckingStupid", "LifeProTips", "longevity", "MapPorn", "mildlyinteresting", 
        "notebooklm", "productivity", "Showerthoughts", "starterpacks", "tragedeigh", 
        "trashy", "Udemy", "WatchPeopleDieInside", "Whatcouldgowrong"
    ]
}

# Add an "All" category that includes all unique subreddits from other categories
all_subs = set()
for subs in SUBREDDIT_CATEGORIES.values():
    all_subs.update(subs)
SUBREDDIT_CATEGORIES["All"] = sorted(list(all_subs))
# --- End Category Definitions ---

# Load environment variables
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API")

@st.cache_resource
def get_reddit_client() -> RedditClient:
    """Create or get a cached Reddit client instance."""
    return RedditClient(user_agent="InsightHub/1.0")

@st.cache_resource
def get_youtube_client():
    """Create or get a cached YouTube API client instance."""
    if not API_KEY:
        return None # Return None if API_KEY is not available
    return build("youtube", "v3", developerKey=API_KEY)

def fetch_videos_from_channels(channels: list[str], max_results_per_channel: int):
    youtube = get_youtube_client()
    if not youtube:
        st.error("YouTube client could not be initialized. Check API Key.")
        return []
        
    videos_list = [] 
    for channel_name in channels:
        try:
            search_response = youtube.search().list(
                q=channel_name, part="id,snippet", type="channel", maxResults=1
            ).execute()
            
            if not search_response.get("items"):
                st.warning(f"Channel '{channel_name}' not found.")
                continue
            channel_id = search_response["items"][0]["id"]["channelId"]

            video_search_response = youtube.search().list(
                channelId=channel_id, part="id,snippet", order="date", type="video", maxResults=max_results_per_channel
            ).execute()
            
            channel_videos = []
            if video_search_response.get("items"):
                for item in video_search_response["items"]:
                    video_id = item["id"]["videoId"]
                    video_title = item["snippet"]["title"]
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    channel_videos.append({
                        'title': video_title, 'url': video_url, 'channel_title': item["snippet"]["channelTitle"]
                    })
            if channel_videos:
                videos_list.extend(channel_videos)
            else:
                st.info(f"No videos found for channel '{channel_name}' (ID: {channel_id}).")
        except HttpError as e:
            error_content = e.content.decode() if e.content else "No details"
            st.error(f"YouTube API Error for '{channel_name}': {e.resp.status} {e.reason}. Details: {error_content}")
        except Exception as e:
            st.error(f"Unexpected error processing channel '{channel_name}': {str(e)}")
    return videos_list

def main():
    st.set_page_config(layout="wide")
    st.title("InsightHub: Reddit & YouTube Aggregator")
    st.markdown("Fetch and list URLs from your favorite subreddits and YouTube channels.")

    # Initialize session state
    if 'selected_posts' not in st.session_state:
        st.session_state.selected_posts = set()
    if 'all_posts' not in st.session_state:
        st.session_state.all_posts = []
    if 'copied_text' not in st.session_state: # Ensure copied_text is initialized
        st.session_state.copied_text = ""
    if 'youtube_videos' not in st.session_state: # Ensure youtube_videos is initialized
        st.session_state.youtube_videos = []
    if 'youtube_copied_text' not in st.session_state: # Ensure youtube_copied_text is initialized
        st.session_state.youtube_copied_text = ""

    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        selected_category = st.selectbox(
            "Select Subreddit Category",
            options=list(SUBREDDIT_CATEGORIES.keys()),
            index=list(SUBREDDIT_CATEGORIES.keys()).index("All")
        )
        default_subreddits = "\\n".join(SUBREDDIT_CATEGORIES[selected_category])
        subreddits_input = st.text_area(
            "Subreddits (one per line)", value=default_subreddits, 
            key=f"subreddits_textarea_{selected_category}",
            help="Subreddits in the selected category. You can edit this list."
        ).strip()

        timeframe = st.selectbox(
            "Select Timeframe", options=["week", "month", "year", "all"], index=0,
            help="Timeframe for fetching top posts."
        )
        post_limit = st.number_input(
            "Posts per Subreddit", min_value=1, max_value=100, value=10,
            help="Number of top posts to fetch from each subreddit."
        )
        fetch_button = st.button("🔄 Fetch Reddit Posts", type="primary", use_container_width=True)

        # --- Rewritten Save to File section for Reddit URLs ---
        if st.session_state.get('selected_posts') and st.session_state.selected_posts:
            st.sidebar.divider()
            st.sidebar.header(f"Selected Reddit URLs ({len(st.session_state.selected_posts)})")
            if st.sidebar.button("💾 Save Selected URLs to File", use_container_width=True, key="save_selected_urls_sidebar"):
                output_dir = "reddit_posts"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(output_dir, f"reddit_urls_{timestamp}.txt")
                
                try:
                    with open(filename, "w", encoding="utf-8") as f:
                        for post_url in sorted(list(st.session_state.selected_posts)):
                            f.write(f"{post_url}\\n")
                    st.sidebar.success(f"✅ Saved to {filename}")
                    
                    preview_text = "\\n".join(sorted(list(st.session_state.selected_posts))[:5])
                    if len(st.session_state.selected_posts) > 5:
                        preview_text += "\\n..."
                    st.sidebar.text_area("Saved URLs (preview)", preview_text, height=100, disabled=True, key="save_preview")
                except Exception as e_save:
                    st.sidebar.error(f"Error saving file: {e_save}")
        # --- End Rewritten Save to File section ---

    # Reddit Post Fetching Logic
    if fetch_button:
        subreddits = [sub.strip() for sub in subreddits_input.split('\\n') if sub.strip()]
        if not subreddits:
            st.warning("Please enter at least one subreddit.")
        else:
            client = get_reddit_client()
            all_posts_data = []
            st.session_state.all_posts = [] # Clear previous results before new fetch
            st.session_state.selected_posts.clear() # Clear selections as well

            progress_bar = st.progress(0, text="Fetching Reddit posts...")
            for i, subreddit_name in enumerate(subreddits):
                posts_list = []
                try:
                    if timeframe == "week":
                        posts_list = client.get_top_weekly_posts(subreddit_name, post_limit)
                    elif timeframe == "month":
                        posts_list = client.get_top_monthly_posts(subreddit_name, post_limit)
                    else: # "year", "all"
                        posts_list = client._get_top_posts(subreddit_name, timeframe, post_limit)
                    
                    if posts_list:
                        all_posts_data.extend(posts_list)
                        # st.toast(f"Fetched {len(posts_list)} posts from r/{subreddit_name}", icon="✅") # Can be too many toasts
                    # else:
                        # st.toast(f"No posts found for r/{subreddit_name}", icon="ℹ️")
                except Exception as e_fetch:
                    st.error(f"Failed to fetch posts from r/{subreddit_name}: {e_fetch}") # This will show Pydantic errors
                progress_bar.progress((i + 1) / len(subreddits), text=f"Fetching from r/{subreddit_name}...")
                if len(subreddits) > 1: # Only sleep if fetching from multiple to avoid unnecessary delay for single subreddit
                    time.sleep(0.5) # Reduced sleep time slightly
            
            progress_bar.empty()
            try:
                st.session_state.all_posts = sorted(all_posts_data, key=lambda x: x.score if hasattr(x, 'score') and x.score is not None else 0, reverse=True)
            except TypeError:
                st.session_state.all_posts = all_posts_data
                st.warning("Could not sort posts by score due to data issues.")

            if st.session_state.all_posts:
                st.success(f"✅ Fetched a total of {len(st.session_state.all_posts)} posts from {len(subreddits)} subreddits.")
            else:
                st.info("No Reddit posts were fetched. Check for errors above if subreddits were provided.")
            st.rerun() # Rerun to update the display with fetched posts

    # --- Rewritten Reddit Bulk Actions and Post Display ---
    if st.session_state.get('all_posts'):
        st.markdown("###  Reddit Post URLs")
        
        col_select_all, col_deselect_all, col_count, col_copy = st.columns([0.2, 0.2, 0.3, 0.3])

        with col_select_all:
            if st.button("Select All", key="select_all_reddit", use_container_width=True):
                for post in st.session_state.all_posts:
                    if hasattr(post, 'url') and post.url:
                        st.session_state.selected_posts.add(post.url)
                st.rerun()

        with col_deselect_all:
            if st.button("Deselect All", key="deselect_all_reddit", use_container_width=True):
                st.session_state.selected_posts.clear()
                st.rerun()

        with col_count:
            st.markdown(f"**{len(st.session_state.selected_posts)}** selected")

        with col_copy:
            copy_button_disabled = not bool(st.session_state.selected_posts)
            if st.button("📋 Copy Selected URLs", key="copy_selected_reddit", use_container_width=True, disabled=copy_button_disabled):
                if st.session_state.selected_posts:
                    sorted_selected_urls = sorted(list(st.session_state.selected_posts))
                    urls_to_copy = "\\n".join(sorted_selected_urls)
                    st.code(urls_to_copy, language=None)
                    st.toast("Selected URLs ready in text box below!", icon="📋")
                # No need for an else here as button is disabled if no selection

        st.divider()
        
        if not st.session_state.all_posts:
            st.info("No Reddit posts to display. Try fetching some posts using the sidebar.")
        else:
            for idx, post_item in enumerate(st.session_state.all_posts):
                # Check if post_item is a valid object with a URL attribute
                if hasattr(post_item, 'url') and isinstance(post_item.url, str) and post_item.url:
                    display_col1, display_col2 = st.columns([0.05, 0.95], gap="small")
                    with display_col1:
                        is_selected_now = st.checkbox(
                            " ", 
                            value=(post_item.url in st.session_state.selected_posts),
                            key=f"select_reddit_{idx}_{post_item.url}",
                            label_visibility="collapsed"
                        )
                    with display_col2:
                        st.markdown(f"[{post_item.url}]({post_item.url})")

                    if is_selected_now and post_item.url not in st.session_state.selected_posts:
                        st.session_state.selected_posts.add(post_item.url)
                        # No need to rerun for individual checkbox, count updates automatically on next interaction
                    elif not is_selected_now and post_item.url in st.session_state.selected_posts:
                        st.session_state.selected_posts.remove(post_item.url)
                        # No need to rerun for individual checkbox
                else:
                    # This indicates a problem with the data in st.session_state.all_posts
                    st.warning(f"Skipping display of an invalid post item (index: {idx}). Check data fetching process.")
    # --- End Rewritten Reddit Bulk Actions and Post Display ---

    # --- YouTube Section ---
    st.markdown("---") 
    st.header("YouTube Latest Video URLs")

    if not API_KEY:
        st.warning("YouTube API Key (YOUTUBE_API) not found in .env. Add it for YouTube functionality.")
    else:
        DEFAULT_YOUTUBE_CHANNEL_NAMES = "AI Jason,David Ondrej,Zen van Riel"
        youtube_channel_names_str = st.text_input(
            "Enter YouTube Channel Names (comma-separated):",
            value=DEFAULT_YOUTUBE_CHANNEL_NAMES,
            help="e.g., AI Jason,David Ondrej,Zen van Riel.",
            key="youtube_channel_names_input"
        )
        num_videos_to_fetch = st.number_input(
            "Number of latest videos per channel:",
            min_value=1, max_value=50, value=3, # Reduced default for quicker tests
            key="youtube_num_videos_input"
        )

        if st.button("Fetch YouTube Videos", key="fetch_youtube_videos_button", use_container_width=True):
            if not youtube_channel_names_str:
                st.warning("Please enter at least one YouTube Channel Name.")
                st.session_state.youtube_videos = []
            else:
                channel_names = [name.strip() for name in youtube_channel_names_str.split(',') if name.strip()]
                if not channel_names:
                    st.warning("No valid Channel Names entered.")
                    st.session_state.youtube_videos = []
                else:
                    with st.spinner("Fetching YouTube videos..."):
                        fetched_videos = fetch_videos_from_channels(
                            channels=channel_names, 
                            max_results_per_channel=num_videos_to_fetch
                        )
                        st.session_state.youtube_videos = fetched_videos
                        if not fetched_videos:
                            st.info("No YouTube videos found for the given channels or an error occurred.")
                        else:
                            st.success(f"Fetched {len(fetched_videos)} YouTube videos.")
                        st.rerun()
    
    if st.session_state.get('youtube_videos'):
        st.subheader("Fetched YouTube Video URLs")
        if not st.session_state.youtube_videos:
            st.info("No YouTube videos to display.")
        else:
            if st.button("📋 Copy YouTube URLs", key="copy_youtube_urls", use_container_width=True):
                youtube_urls_to_copy = "\n".join([video['url'] for video in st.session_state.youtube_videos if isinstance(video, dict) and video.get('url')])
                st.session_state.youtube_copied_text = youtube_urls_to_copy # Store in session state
                st.toast("YouTube URLs ready in text box below!", icon="📋")

            if st.session_state.youtube_copied_text: # Display if there's text to show
                st.code(st.session_state.youtube_copied_text, language=None)
            
            st.markdown("---") # Add a separator

            for video in st.session_state.youtube_videos:
                if isinstance(video, dict) and video.get('url'):
                    st.markdown(f"[{video['url']}]({video['url']}) - *{video.get('channel_title','Unknown Channel')}*") # Restored channel title
                else:
                    st.warning("Skipping display of an invalid YouTube video item.")
    
if __name__ == "__main__":
    main()
