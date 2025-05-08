"""Streamlit frontend for Reddit Weekly Top."""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from typing import List, Tuple
import datetime
from googleapiclient.discovery import build
from dotenv import load_dotenv

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

# Initialize the Reddit client
@st.cache_resource
def get_reddit_client() -> RedditClient:
    """Create or get a cached Reddit client instance."""
    return RedditClient(user_agent="InsightHub/1.0")

def format_post(post: RedditPost) -> Tuple[str, dict]:
    """Format a post for display and return its metadata."""
    created_date = post.created_utc.strftime("%Y-%m-%d %H:%M")
    markdown = f"""
    ### [{post.title}]({post.url})
    **Score:** {post.score} | **Author:** u/{post.author} | **Posted:** {created_date}
    
    {post.selftext[:300] + '...' if len(post.selftext) > 300 else post.selftext}
    """
    metadata = {
        "url": post.url,
        "score": post.score,
        "author": post.author,
        "created_utc": post.created_utc,
        "subreddit": post.subreddit,
        "is_selected": False  # For tracking selected posts
    }
    return markdown, metadata

def toggle_all_posts(posts: List[RedditPost], select: bool) -> None:
    """Select or deselect all posts."""
    if select:
        st.session_state.selected_posts.update(post.url for post in posts)
    else:
        st.session_state.selected_posts.clear()

# Load environment variables
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API")

@st.cache_resource
def get_youtube_client():
    """Create or get a cached YouTube API client instance."""
    return build("youtube", "v3", developerKey=API_KEY)

def fetch_videos_from_channels(channels, timeframe):
    """Fetch videos from specified YouTube channels within the given timeframe."""
    youtube = get_youtube_client()
    videos = []
    one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    for channel_name in channels:
        try:
            search_response = youtube.search().list(
                q=channel_name,
                part="snippet",
                type="channel",
                maxResults=1
            ).execute()

            if not search_response["items"]:
                st.warning(f"No channel found with the name '{channel_name}'.")
                continue

            channel_id = search_response["items"][0]["id"]["channelId"]
            channel_response = youtube.channels().list(
                part="contentDetails",
                id=channel_id
            ).execute()

            uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            next_page_token = None

            while True:
                playlist_response = youtube.playlistItems().list(
                    part="snippet",
                    playlistId=uploads_playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()

                for item in playlist_response["items"]:
                    video_title = item["snippet"]["title"]
                    video_url = f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
                    published_at = item["snippet"]["publishedAt"]
                    published_date = datetime.datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")

                    if published_date >= one_week_ago:
                        videos.append({"title": video_title, "url": video_url, "published_at": published_date})

                next_page_token = playlist_response.get("nextPageToken")
                if not next_page_token:
                    break

        except Exception as e:
            st.error(f"Error fetching videos from {channel_name}: {str(e)}")

    return videos

def main():
    st.title("Reddit Weekly Top")
    st.markdown("""
    Fetch and analyze top posts from your favorite subreddits.
    Select the posts you want to save for further analysis.
    """)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Category Selector
        selected_category = st.selectbox(
            "Select Subreddit Category",
            options=list(SUBREDDIT_CATEGORIES.keys()),
            index=list(SUBREDDIT_CATEGORIES.keys()).index("All") # Default to "All"
        )
        
        # Update text area based on selected category
        default_subreddits = "\n".join(SUBREDDIT_CATEGORIES[selected_category])
        
        subreddits_input = st.text_area(
            "Subreddits (one per line)",
            value=default_subreddits,
            key=f"subreddits_textarea_{selected_category}", # Use category in key to force update
            help="Subreddits in the selected category. You can edit this list."
        ).strip()
        
        # Split the potentially edited list
        subreddits = subreddits_input.split('\n') if subreddits_input else []
        
        timeframe = st.selectbox(
            "Select timeframe",
            options=["week", "month"],
            index=0,
            help="Time period for top posts"
        )
        
        post_limit = st.slider(
            "Posts per subreddit",
            min_value=1,
            max_value=50,
            value=10,
            help="Maximum number of posts to fetch per subreddit"
        )

        view_mode = st.radio(
            "View Mode",
            options=["Detailed View", "List View"],
            index=0,
            help="Choose how to display the posts"
        )
        
        fetch_button = st.button("🔄 Fetch Posts", type="primary")
    
    # Initialize session state for selected posts if not exists
    if 'selected_posts' not in st.session_state:
        st.session_state.selected_posts = set()
    if 'all_posts' not in st.session_state:
        st.session_state.all_posts = []
    
    if fetch_button:
        client = get_reddit_client()
        all_posts = []
        
        # Show progress bar while fetching
        progress = st.progress(0)
        for i, subreddit in enumerate(subreddits):
            try:
                if timeframe == "week":
                    posts = client.get_top_weekly_posts(subreddit.strip(), post_limit)
                else:
                    posts = client.get_top_monthly_posts(subreddit.strip(), post_limit)
                all_posts.extend(posts)
                progress.progress((i + 1) / len(subreddits))
            except Exception as e:
                st.error(f"Error fetching posts from r/{subreddit}: {str(e)}")
        
        progress.empty()
        st.session_state.all_posts = sorted(all_posts, key=lambda x: x.score, reverse=True)
        
        if all_posts:
            st.success(f"✅ Fetched {len(all_posts)} posts from {len(subreddits)} subreddits")
    
    # Display toolbar with bulk actions if there are posts
    if st.session_state.all_posts:
        st.markdown("### 🔄 Bulk Actions")
        col1, col2, col3, col4 = st.columns([0.2, 0.2, 0.3, 0.3])
        with col1:
            if st.button("Select All"):
                toggle_all_posts(st.session_state.all_posts, True)
        with col2:
            if st.button("Deselect All"):
                toggle_all_posts(st.session_state.all_posts, False)
        with col3:
            selected_count = len(st.session_state.selected_posts)
            st.markdown(f"**{selected_count}** posts selected")
        with col4:
            if selected_count > 0:
                if st.button("📋 Copy Selected URLs"):
                    selected_posts = [p for p in st.session_state.all_posts if p.url in st.session_state.selected_posts]
                    urls = "\n".join(p.url for p in selected_posts)
                    st.code(urls, language="text")
        
        st.divider()

    # Display posts based on view mode
    if st.session_state.all_posts:
        for post in st.session_state.all_posts:
            if view_mode == "List View":
                col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
                with col1:
                    is_selected = st.checkbox(
                        "✓",
                        key=f"select_{post.url}",
                        value=post.url in st.session_state.selected_posts
                    )
                with col2:
                    st.markdown(f"[{post.title}]({post.url})")
                with col3:
                    st.markdown(f"↑ {post.score}")
            else:
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    markdown, metadata = format_post(post)
                    st.markdown(markdown)
                with col2:
                    is_selected = st.checkbox(
                        "Select",
                        key=f"select_{post.url}",
                        value=post.url in st.session_state.selected_posts
                    )
            
            if is_selected:
                st.session_state.selected_posts.add(post.url)
            elif post.url in st.session_state.selected_posts:
                st.session_state.selected_posts.remove(post.url)
            
            if view_mode == "Detailed View":
                st.divider()
        
        # Show export options for selected posts
        if st.session_state.selected_posts:
            st.sidebar.divider()
            st.sidebar.header("Selected Posts")
            st.sidebar.info(f"✨ {len(st.session_state.selected_posts)} posts selected")
            
            if st.sidebar.button("💾 Save to File", use_container_width=True):
                # Filter selected posts
                selected_posts = [p for p in st.session_state.all_posts if p.url in st.session_state.selected_posts]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"reddit_urls_{timestamp}.txt"
                
                # Save to file
                with open(f"reddit_posts/{filename}", "w", encoding="utf-8") as f:
                    for post in selected_posts:
                        f.write(f"{post.url}\n")
                
                st.sidebar.success(f"✅ Saved to reddit_posts/{filename}")
                
                # Show preview
                st.sidebar.markdown("### Preview")
                for post in selected_posts:
                    st.sidebar.text(post.url)

    # Add YouTube integration to the sidebar
    with st.sidebar:
        st.header("YouTube Configuration")
        youtube_channels_input = st.text_area(
            "YouTube Channels (one per line)",
            value="AI Jason\nDavid Ondrej\nZen van Riel",
            help="Enter the names of YouTube channels to fetch videos from."
        ).strip()

        youtube_channels = youtube_channels_input.split('\n') if youtube_channels_input else []

        fetch_youtube_button = st.button("Fetch YouTube Videos", type="primary")

    if fetch_youtube_button:
        youtube_videos = fetch_videos_from_channels(youtube_channels, timeframe)
        if youtube_videos:
            st.success(f"Fetched {len(youtube_videos)} videos from {len(youtube_channels)} channels.")
            for video in youtube_videos:
                st.markdown(f"- [{video['title']}]({video['url']}) (Published: {video['published_at']})")

if __name__ == "__main__":
    main()
