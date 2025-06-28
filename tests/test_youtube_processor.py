import pytest
from unittest.mock import patch, MagicMock
from src.youtube_processor import YouTubeProcessor

@pytest.fixture
def processor():
    """Provides a YouTubeProcessor instance for tests."""
    return YouTubeProcessor()

def test_youtubeprocessor_class_exists():
    """
    Tests that the YouTubeProcessor class can be imported.
    """
    try:
        from src.youtube_processor import YouTubeProcessor
    except ImportError as e:
        pytest.fail(f"Failed to import YouTubeProcessor: {e}")

@pytest.mark.parametrize("url, expected_id", [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=60s", "dQw4w9WgXcQ"),
    ("invalid-url", None),
])
def test_get_video_id(processor, url, expected_id):
    """Tests the video ID extraction from the standard URL format."""
    assert processor.get_video_id(url) == expected_id

@patch('src.youtube_processor.YouTubeProcessor.transcribe_audio')
@patch('src.youtube_processor.YouTubeProcessor.download_audio')
@patch('src.youtube_processor.os.path.exists')
@patch('src.youtube_processor.os.remove')
def test_get_transcript_success(mock_remove, mock_exists, mock_download, mock_transcribe, processor):
    """Tests successful transcript fetching using the local workflow."""
    mock_download.return_value = "/tmp/fake_audio.mp3"
    mock_transcribe.return_value = "This is the transcript."
    mock_exists.return_value = True

    url = "https://www.youtube.com/watch?v=valid_id"
    transcript = processor.get_transcript(url, model_size="base")

    mock_download.assert_called_with(url)
    mock_transcribe.assert_called_with("/tmp/fake_audio.mp3", model_size="base")
    assert transcript == "This is the transcript."
    mock_exists.assert_called_with("/tmp/fake_audio.mp3")
    mock_remove.assert_called_with("/tmp/fake_audio.mp3")

def test_get_transcript_invalid_url(processor):
    """Tests transcript fetching with an invalid YouTube URL."""
    with pytest.raises(ValueError, match="Invalid YouTube URL provided."):
        processor.get_transcript("not-a-youtube-url")

@patch('src.youtube_processor.YouTubeProcessor.download_audio', side_effect=ValueError("Download failed"))
def test_get_transcript_download_fails(mock_download, processor):
    """Tests when the audio download fails."""
    url = "https://www.youtube.com/watch?v=fail_id"
    with pytest.raises(ValueError, match="Failed to get transcript: Download failed"):
        processor.get_transcript(url)

@patch('src.youtube_processor.os.path.getsize')
@patch('src.youtube_processor.os.path.exists')
@patch('src.youtube_processor.yt_dlp.YoutubeDL')
def test_download_audio_success(mock_yt_dlp, mock_exists, mock_getsize, processor):
    """Tests successful audio download using yt-dlp."""
    # Configure the mock to simulate yt-dlp's behavior
    mock_ydl_instance = mock_yt_dlp.return_value.__enter__.return_value
    mock_ydl_instance.extract_info.return_value = {}  # Simulate successful extraction
    mock_exists.return_value = True
    mock_getsize.return_value = 1024 # Simulate a non-empty file
    
    # The path we expect the method to generate and use
    temp_audio_path = "/tmp/audio.mp3"

    # We need to mock the tempfile creation to return a predictable path
    with patch('src.youtube_processor.tempfile.NamedTemporaryFile') as mock_tempfile:
        # Make the mock tempfile object have a 'name' attribute
        mock_tempfile.return_value.name = temp_audio_path
        
        url = "https://www.youtube.com/watch?v=some_video_id"
        downloaded_path = processor.download_audio(url)

        # Check that YoutubeDL was initialized with the correct options
        expected_opts = {
            'format': 'bestaudio/best',
            'outtmpl': temp_audio_path,
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        mock_yt_dlp.assert_called_with(expected_opts)

        # Check that extract_info was called with the URL
        mock_ydl_instance.extract_info.assert_called_with(url, download=True)
        
        # Check that the method returns the correct path
        assert downloaded_path == temp_audio_path

@patch('src.youtube_processor.faster_whisper.WhisperModel')
def test_transcribe_audio_success(mock_whisper_model, processor):
    """Tests successful audio transcription using faster-whisper."""
    # Configure the mock model to simulate transcription
    mock_model_instance = mock_whisper_model.return_value
    
    # The 'transcribe' method of the model returns an iterator of segments and info
    mock_segments = [MagicMock(text="Hello world.")]
    mock_info = MagicMock() # Not used in the implementation, but part of the return value
    mock_model_instance.transcribe.return_value = (mock_segments, mock_info)

    audio_path = "/tmp/audio.mp3"
    model_size = "tiny"
    transcript = processor.transcribe_audio(audio_path, model_size)

    # Check that WhisperModel was initialized with the correct size
    mock_whisper_model.assert_called_with(model_size)

    # Check that transcribe was called on the instance with the audio path
    mock_model_instance.transcribe.assert_called_with(audio_path)

    # Check that the transcript is correctly joined from the segments
    assert transcript == "Hello world."
