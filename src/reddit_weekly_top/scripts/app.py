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
    if 'generated_ai_prompt' not in st.session_state:
        st.session_state.generated_ai_prompt = ""

    # Sidebar for configuration
    with st.sidebar:
        st.header("NotebookLM Podcast Prompt Generator")
        prompt_category_options = list(SUBREDDIT_CATEGORIES.keys())
        if "All" in prompt_category_options:
            prompt_category_options.remove("All")
        prompt_selected_category = st.selectbox(
            "Aihealue/Kategoria",
            options=prompt_category_options,
            index=0,
            key="notebooklm_prompt_category_select"
        )
        prompt_tone = st.text_input(
            "Äänensävy (esim. keskusteleva, asiantunteva, uutistyylinen)",
            value="keskusteleva",
            key="notebooklm_prompt_tone_input"
        )
        prompt_audience = st.text_input(
            "Kohdeyleisö (esim. aloittelija, asiantuntija)",
            value="aloittelija",
            key="notebooklm_prompt_audience_input"
        )
        prompt_structure = st.text_input(
            "Rakenne (esim. kolmiosainen: johdanto, pääkohdat, yhteenveto)",
            value="johdanto, pääkohdat, yhteenveto",
            key="notebooklm_prompt_structure_input"
        )
        prompt_length = st.text_input(
            "Pituustoive (esim. pidä lyhyenä, max 10 min)",
            value="pidä lyhyenä",
            key="notebooklm_prompt_length_input"
        )
        prompt_keywords = st.text_area(
            "Avainsanat / Fokus (valinnainen)",
            placeholder="esim. tekoälyn trendit, viimeisimmät innovaatiot",
            key="notebooklm_prompt_keywords_input"
        )
        # Promptin generointi
        context_parts = []
        if prompt_selected_category:
            context_parts.append(f"Aihe: {prompt_selected_category}.")
        if prompt_tone:
            context_parts.append(f"Äänensävy: {prompt_tone}.")
        if prompt_audience:
            context_parts.append(f"Kohdeyleisö: {prompt_audience}.")
        if prompt_structure:
            context_parts.append(f"Rakenne: {prompt_structure}.")
        if prompt_length:
            context_parts.append(f"Pituus: {prompt_length}.")
        if prompt_keywords:
            focus_text = prompt_keywords.replace('"', "'").replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('\u2028', ' ').replace('\u2029', ' ').replace('\xa0', ' ').replace('\ufeff', ' ').replace('\u200b', ' ').replace('\u200c', ' ').replace('\u200d', ' ').replace('\u2060', ' ').replace('\uFEFF', ' ').replace('\u00A0', ' ').replace('\u202F', ' ').replace('\u205F', ' ').replace('\u3000', ' ').replace('\u180E', ' ').replace('\u2000', ' ').replace('\u2001', ' ').replace('\u2002', ' ').replace('\u2003', ' ').replace('\u2004', ' ').replace('\u2005', ' ').replace('\u2006', ' ').replace('\u2007', ' ').replace('\u2008', ' ').replace('\u2009', ' ').replace('\u200A', ' ').replace('\u2028', ' ').replace('\u2029', ' ').replace('\u202F', ' ').replace('\u205F', ' ').replace('\u3000', ' ').strip()[:100]
            context_parts.append(f"Fokus: {focus_text}.")
        context = " ".join(context_parts)
        final_prompt = f"Task: Luo podcast. {context} Output: Podcast-skripti. CRITICAL: Käytä VAIN annettuja lähde-URL:eja.".strip()
        # Pituusrajoitus
        if len(final_prompt) > 500:
            final_prompt = final_prompt[:497] + "..."
        st.markdown(f"**Generoitu NotebookLM-podcast-kehote:**")
        st.text_area("Prompt", value=final_prompt, height=100, max_chars=500, key="notebooklm_generated_prompt")
        st.caption(f"Merkkimäärä: {len(final_prompt)}/500")
        st.divider()
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

        # --- AI Prompt Generator Section ---
        st.sidebar.divider()
        st.sidebar.header("AI Prompt Generator")
        
        prompt_category_options = list(SUBREDDIT_CATEGORIES.keys())
        if "All" in prompt_category_options: # Remove "All" if it's not suitable for specific prompt generation
            prompt_category_options.remove("All")

        prompt_selected_category = st.sidebar.selectbox(
            "Select Category for Prompt",
            options=prompt_category_options,
            index=0, # Default to the first category
            key="prompt_category_select"
        )

        prompt_length = st.sidebar.text_input(
            "Desired Podcast Length (e.g., '10-15 minutes', 'short')",
            value="around 10-15 minutes",
            key="prompt_length_input"
        )

        prompt_tone = st.sidebar.text_input(
            "Desired Podcast Tone (e.g., 'informative', 'conversational')",
            value="informative and engaging",
            key="prompt_tone_input"
        )

        prompt_keywords = st.sidebar.text_area(
            "Optional: Keywords/Focus Points",
            placeholder="e.g., latest breakthroughs, beginner-friendly explanations, future trends",
            key="prompt_keywords_input"
        )

        if st.sidebar.button("✨ Generate AI Prompt", key="generate_ai_prompt_button", use_container_width=True):
            # --- New prompt generation based on podcast_prompt.md principles ---
            task = "Task: Create podcast."

            context_parts = []
            if prompt_selected_category:
                context_parts.append(f"Topic: {prompt_selected_category}.")
            if prompt_tone:
                context_parts.append(f"Tone: {prompt_tone}.")
            if prompt_length:
                # podcast_prompt.md notes that specific times can be unreliable.
                # Phrasing as "Aim for..." or using descriptive terms.
                context_parts.append(f"Length goal: {prompt_length}.")

            context = " ".join(context_parts)

            reference_parts = ["Ref: Structure: intro, key insights, summary."]
            if prompt_keywords:
                sanitized_keywords = prompt_keywords.replace('"', "'").replace('\\n', ' ').strip()
                if sanitized_keywords:
                    # Truncate keywords to ensure overall prompt stays short
                    reference_parts.append(f"Focus on: {sanitized_keywords[:120]}.")
            
            reference_parts.append("Output: Podcast script.")
            # Emphasize source adherence strongly, as per podcast_prompt.md
            reference_parts.append("CRITICAL: Use ONLY provided source URLs for content.")
            
            reference = " ".join(reference_parts)

            # Combine into a single, compact prompt string
            final_prompt = f"{task} {context} {reference}".strip()

            # Fallback: If the prompt is unexpectedly long, create a very minimal version.
            # This should ideally not be hit with the current structure and keyword truncation.
            if len(final_prompt) > 490: # Leave a small buffer for safety
                simplified_focus = ""
                if prompt_keywords:
                    focus_text = prompt_keywords.replace('"', "'").replace('\n', ' ').strip()[:50]
                    simplified_focus = f"Focus: {focus_text}."
                
                final_prompt = (f"Podcast on {prompt_selected_category}. {simplified_focus} "
                                f"Tone: {prompt_tone.split(',')[0]}. Structure: intro, insights, summary. "
                                f"Base ONLY on sources.").strip()
                final_prompt = final_prompt[:490] # Hard truncate if still too long

            st.session_state.generated_ai_prompt = final_prompt
            st.toast("AI Prompt generated using podcast_prompt.md guidelines!", icon="✨")
            # --- End of new prompt generation ---

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
    
    # --- Display AI Generated Prompt ---
    if st.session_state.generated_ai_prompt:
        st.markdown("---")
        st.subheader("🤖 Generated AI Prompt for Podcast")
        st.text_area("Copy this prompt for your podcast tool (e.g., NotebookLM):", value=st.session_state.generated_ai_prompt, height=250, key="generated_ai_prompt_display")
        if st.button("📋 Copy Prompt", key="copy_generated_prompt"):
            # This button doesn't automatically copy to clipboard in Streamlit's core
            # It's more of a user cue. For actual clipboard, a component would be needed.
            # However, the text_area itself is easy to copy from.
            st.toast("Prompt ready in the text box for copying!", icon="📋")


if __name__ == "__main__":
    main()
