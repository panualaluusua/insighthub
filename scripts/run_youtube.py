import os
from dotenv import load_dotenv
from src.youtube_processor import YouTubeProcessor

# Load environment variables from .env file
load_dotenv()

def main():
    """
    Runs a test to transcribe a YouTube video using the OpenAI Whisper API.
    """
    test_url = "https://www.youtube.com/watch?v=1Q_MDOWaljk" # Example URL, replace with a suitable one
    
    # Check for OPENAI_API_KEY
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set. Please set it in your .env file.")
        return

    print(f"Attempting to transcribe audio from: {test_url} using OpenAI Whisper API")
    
    processor = YouTubeProcessor()
    try:
        print("\n--- Testing with speed_up=False ---")
        transcript_normal = processor.get_transcript(test_url, model_size="openai", speed_up=False)
        print("Transcript (normal):\n" + transcript_normal[:500] + "..." if len(transcript_normal) > 500 else transcript_normal)
        print("-----------------------------------")

        print("\n--- Testing with speed_up=True ---")
        transcript_sped_up = processor.get_transcript(test_url, model_size="openai", speed_up=True)
        print("Transcript (sped up):\n" + transcript_sped_up[:500] + "..." if len(transcript_sped_up) > 500 else transcript_sped_up)
        print("-----------------------------------")

    except Exception as e:
        print(f"❌ An error occurred during transcription: {e}")

if __name__ == "__main__":
    main()
