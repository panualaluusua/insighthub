import pytest

def test_process_youtube_video_exists():
    """
    Tests that the process_youtube_video function can be imported.
    This is the first, simple test to fail, adhering to TDD.
    """
    try:
        from src.youtube_processor import process_youtube_video
    except ImportError as e:
        pytest.fail(f"Failed to import process_youtube_video: {e}") 