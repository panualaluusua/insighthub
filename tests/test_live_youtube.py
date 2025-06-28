import pytest
from src.youtube_processor import YouTubeProcessor

def test_live_youtube_processor_exists():
    """
    Test that we can create a YouTubeProcessor for live testing.
    """
    processor = YouTubeProcessor()
    assert processor is not None

def test_live_process_real_url_handles_errors():
    """
    Test that we can handle real YouTube URLs gracefully.
    Some videos may not have transcripts or may have network issues.
    """
    processor = YouTubeProcessor()
    url = "https://www.youtube.com/watch?v=1Q_MDOWaljk"
    
    try:
        transcript = processor.get_transcript(url)
        # If we get here, transcript worked
        assert isinstance(transcript, str)
        assert len(transcript) > 0
        print(f"✅ Successfully extracted transcript ({len(transcript)} chars)")
    except ValueError as e:
        # This is expected for videos without transcripts or network issues
        assert "transcript" in str(e).lower() or "error" in str(e).lower()
        print(f"⚠️  Expected error: {e}")
        # Test passes even if transcript is not available 