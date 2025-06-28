import os
from dotenv import load_dotenv
from pytube import YouTube

# Load environment variables from .env file
load_dotenv()

def main():
    """
    Runs a live test to check available captions for a YouTube video.
    """
    test_url = "https://www.youtube.com/watch?v=1Q_MDOWaljk"
    
    print(f"Checking captions for: {test_url}")
    
    try:
        yt = YouTube(test_url)
        print(f"Video Title: {yt.title}")
        print("\\n--- Available Caption Tracks ---")
        for caption in yt.caption_tracks:
            print(caption)
        print("------------------------------")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main() 