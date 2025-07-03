import os
from src.youtube_processor import YouTubeProcessor

# ---
# INSTRUCTIONS:
# 1. Ensure you have ffmpeg installed and available in your PATH.
# 2. Set the following environment variables (in your .env or system):
#    - OPENAI_API_KEY=your_openai_api_key
#    - AUDIO_SPEED_FACTOR=2.0 (or desired speedup)
#    - TRANSCRIPTION_METHOD=openai (or 'local' for faster-whisper)
# 3. Run this script: python test_youtube_transcription_speedup.py
# ---

def main():
    # You can replace this with any public YouTube video URL
    youtube_url = input("Enter a YouTube video URL to transcribe (sped up): ").strip()
    if not youtube_url:
        print("No URL provided. Exiting.")
        return

    processor = YouTubeProcessor()
    print(f"\nTranscribing (sped up) YouTube audio from: {youtube_url}\n")
    try:
        transcript = processor.get_transcript(youtube_url, speed_up=True)
        print("\n--- TRANSCRIPT START ---\n")
        print(transcript)
        print("\n--- TRANSCRIPT END ---\n")
    except Exception as e:
        print(f"Error during transcription: {e}")

if __name__ == "__main__":
    main() 