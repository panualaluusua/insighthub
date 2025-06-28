import argparse
import logging
from src.youtube_processor import YouTubeProcessor

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to run the YouTube video processing script.
    """
    parser = argparse.ArgumentParser(description="Download audio from a YouTube video and transcribe it locally.")
    parser.add_argument("url", help="The full URL of the YouTube video.")
    parser.add_argument(
        "--model", 
        default="tiny", 
        help="The faster-whisper model size to use (e.g., tiny, base, small, medium, large)."
    )
    args = parser.parse_args()

    processor = YouTubeProcessor()

    try:
        logging.info(f"Processing URL: {args.url}")
        logging.info(f"Using Whisper model: {args.model}")
        
        transcript = processor.get_transcript(args.url, model_size=args.model)
        
        logging.info("Transcription completed successfully.")
        print("\n--- TRANSCRIPT ---")
        print(transcript)
        print("------------------\n")

    except ValueError as e:
        logging.error(f"A processing error occurred: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main() 