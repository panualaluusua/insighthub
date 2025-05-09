"""YouTube API client for fetching video data."""

import os
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API")

class YouTubeClient:
    """Client for interacting with YouTube's API."""
    
    def __init__(self):
        """Initialize the YouTube client."""
        self.client = self._get_client()
    
    def _get_client(self):
        """Get or create a YouTube API client instance."""
        if not API_KEY:
            return None
        return build("youtube", "v3", developerKey=API_KEY)
    
    def fetch_videos_from_channels(self, channels: List[str], max_results: int = 10) -> List[Dict]:
        """Fetch latest videos from specified channels.
        
        Args:
            channels: List of channel names to fetch videos from
            max_results: Maximum number of videos per channel
            
        Returns:
            List of video dictionaries containing title, url, and channel_title
        """
        if not self.client:
            raise ValueError("YouTube client could not be initialized. Check API Key.")
            
        videos = []
        for channel_name in channels:
            try:
                channel_id = self._get_channel_id(channel_name)
                if channel_id:
                    channel_videos = self._get_channel_videos(channel_id, max_results)
                    videos.extend(channel_videos)
            except HttpError as e:
                raise Exception(f"YouTube API Error for '{channel_name}': {e.resp.status} {e.reason}")
        
        return videos
    
    def _get_channel_id(self, channel_name: str) -> Optional[str]:
        """Get channel ID from channel name."""
        response = self.client.search().list(
            q=channel_name,
            part="id",
            type="channel",
            maxResults=1
        ).execute()
        
        if not response.get("items"):
            return None
            
        return response["items"][0]["id"]["channelId"]
    
    def _get_channel_videos(self, channel_id: str, max_results: int) -> List[Dict]:
        """Get latest videos from a channel."""
        response = self.client.search().list(
            channelId=channel_id,
            part="id,snippet",
            order="date",
            type="video",
            maxResults=max_results
        ).execute()
        
        videos = []
        video_items = []
        video_id_map = {}
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            video_title = item["snippet"]["title"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_items.append((video_id, video_title, video_url, item["snippet"]["channelTitle"]))
            video_id_map[video_id] = (video_title, video_url, item["snippet"]["channelTitle"])

        # Fetch durations for all video_ids
        if video_items:
            video_ids = [vid[0] for vid in video_items]
            details_response = self.client.videos().list(
                id=','.join(video_ids),
                part="contentDetails"
            ).execute()
            durations = {item["id"]: item["contentDetails"]["duration"] for item in details_response.get("items", [])}

            for video_id, video_title, video_url, channel_title in video_items:
                # Filter by /shorts/ in URL
                if "/shorts/" in video_url:
                    continue
                # Filter by duration < 60s
                duration_iso = durations.get(video_id)
                if duration_iso:
                    try:
                        duration_seconds = parse_duration(duration_iso).total_seconds()
                        if duration_seconds < 60:
                            continue
                    except Exception:
                        pass  # If parsing fails, include the video
                videos.append({
                    'title': video_title,
                    'url': video_url,
                    'channel_title': channel_title
                })
    
        return videos
