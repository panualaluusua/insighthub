import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the API key from the .env file
API_KEY = os.getenv("YOUTUBE_API")

# Function to fetch videos from a YouTube channel
def fetch_videos_from_channel(channel_name):
    try:
        # Build the YouTube API client
        youtube = build("youtube", "v3", developerKey=API_KEY)

        # Search for the channel by name to get the channel ID
        search_response = youtube.search().list(
            q=channel_name,
            part="snippet",
            type="channel",
            maxResults=1
        ).execute()

        if not search_response["items"]:
            print(f"No channel found with the name '{channel_name}'.")
            return

        # Get the channel ID
        channel_id = search_response["items"][0]["id"]["channelId"]

        # Fetch the uploads playlist ID
        channel_response = youtube.channels().list(
            part="contentDetails",
            id=channel_id
        ).execute()

        uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Fetch videos from the uploads playlist
        videos = []
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
                videos.append({"title": video_title, "url": video_url})

            next_page_token = playlist_response.get("nextPageToken")
            if not next_page_token:
                break

        # Print the videos
        for video in videos:
            print(f"{video['title']}: {video['url']}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Test the function
if __name__ == "__main__":
    fetch_videos_from_channel("AI Jason")
