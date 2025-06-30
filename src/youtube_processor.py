from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
import yt_dlp
import tempfile
import faster_whisper
import os
import subprocess
from src.config import TRANSCRIPTION_METHOD, AUDIO_SPEED_FACTOR

class YouTubeProcessor:
    """
    A class to process YouTube videos by fetching their transcripts.
    """

    def download_audio(self, url: str) -> str:
        """
        Downloads the audio from a YouTube URL to a temporary file.

        Args:
            url: The URL of the YouTube video.

        Returns:
            The file path to the downloaded audio file.
        
        Raises:
            ValueError: If the URL is invalid.
        """
        video_id = self.get_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL provided.")

        import uuid
        temp_dir = tempfile.gettempdir()
        temp_filename = f"youtube_audio_{uuid.uuid4().hex[:8]}.%(ext)s"
        temp_audio_path = os.path.join(temp_dir, temp_filename)

        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio',
            'outtmpl': temp_audio_path,
            'noplaylist': True,
            'no_check_certificate': True,
            'force_overwrites': True,
            'rm_cachedir': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)
            
            # Find the actual downloaded file (yt-dlp replaces %(ext)s with the actual extension)
            temp_dir = tempfile.gettempdir()
            base_name = temp_filename.replace('.%(ext)s', '')
            downloaded_files = [f for f in os.listdir(temp_dir) if f.startswith(base_name)]
            
            if not downloaded_files:
                raise ValueError(f"No audio file was created with pattern {base_name}*")
            
            actual_audio_path = os.path.join(temp_dir, downloaded_files[0])
            
            # Check if the file exists and is not empty
            if not os.path.exists(actual_audio_path):
                raise ValueError(f"Audio file was not created at {actual_audio_path}")
            elif os.path.getsize(actual_audio_path) == 0:
                raise ValueError(f"Audio download resulted in an empty file at {actual_audio_path}. File exists but has 0 bytes.")

            return actual_audio_path
        except Exception as e:
            raise ValueError(f"Failed to download audio: {e}")

    def transcribe_audio_local(self, audio_path: str, model_size: str = "tiny") -> str:
        """
        Transcribes an audio file using faster-whisper.

        Args:
            audio_path: The path to the audio file.
            model_size: The size of the Whisper model to use 
                        (e.g., 'tiny', 'base', 'small', 'medium', 'large').

        Returns:
            The full transcribed text as a single string.
        
        Raises:
            ValueError: If transcription fails.
        """
        try:
            model = faster_whisper.WhisperModel(model_size)
            segments, _ = model.transcribe(audio_path)
            # Concatenate the text from all segments
            full_transcript = "".join([segment.text for segment in segments])
            return full_transcript.strip()
        except Exception as e:
            raise ValueError(f"Failed to transcribe audio with faster-whisper: {e}")

    def transcribe_audio_openai(self, audio_path: str) -> str:
        """
        Transcribes an audio file using OpenAI Whisper API.

        Args:
            audio_path: The path to the audio file.

        Returns:
            The full transcribed text as a single string.

        Raises:
            ValueError: If transcription fails or API key is missing.
        """
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")

        client = OpenAI(api_key=api_key)
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return transcript.text
        except Exception as e:
            raise ValueError(f"Failed to transcribe audio with OpenAI Whisper API: {e}")

    def speed_up_audio(self, input_file: str, output_file: str, speed_factor: float = 2.0):
        """
        Speeds up an audio file using ffmpeg.

        Args:
            input_file: Path to the input audio file.
            output_file: Path for the sped-up output audio file.
            speed_factor: Factor by which to speed up the audio (e.g., 2.0 for double speed).
        
        Raises:
            ValueError: If ffmpeg command fails.
        """
        cmd = [
            'ffmpeg', '-i', input_file,
            '-filter:a', f'atempo={speed_factor}',
            '-c:a', 'aac', '-b:a', '192k',
            output_file
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise ValueError(f"ffmpeg failed: {e.stderr}")
        except FileNotFoundError:
            raise ValueError("ffmpeg not found. Please ensure ffmpeg is installed and in your PATH.")

    def get_video_id(self, url: str) -> str | None:
        """
        Extracts the YouTube video ID from a standard watch URL.
        e.g., https://www.youtube.com/watch?v=VIDEO_ID
        """
        try:
            parsed_url = urlparse(url)
            if "youtube.com" not in parsed_url.netloc:
                return None

            if parsed_url.path == "/watch":
                video_id = parse_qs(parsed_url.query).get("v")
                return video_id[0] if video_id else None
                
        except (AttributeError, TypeError, IndexError):
            return None
        
        return None

    def get_transcript(self, url: str, model_size: str = "tiny", speed_up: bool = False) -> str:
        """
        Fetches the transcript for a given YouTube URL by downloading the audio
        and transcribing it locally.

        Args:
            url: The URL of the YouTube video.
            model_size: The size of the Whisper model to use.

        Returns:
            The full transcript as a single string.

        Raises:
            ValueError: If the URL is invalid or transcription fails.
        """
        audio_path = None
        sped_up_audio_path = None
        try:
            # Download audio
            audio_path = self.download_audio(url)
            
            if speed_up:
                # Speed up the audio if requested
                import uuid
                temp_dir = tempfile.gettempdir()
                sped_up_audio_path = os.path.join(temp_dir, f"sped_up_youtube_audio_{uuid.uuid4().hex[:8]}.m4a")
                self.speed_up_audio(audio_path, sped_up_audio_path)
                audio_to_transcribe = sped_up_audio_path
            else:
                audio_to_transcribe = audio_path

            # Transcribe audio
            if TRANSCRIPTION_METHOD == "openai":
                transcript = self.transcribe_audio_openai(audio_to_transcribe)
            else:
                transcript = self.transcribe_audio_local(audio_to_transcribe, model_size=model_size)
            
            return transcript
        except Exception as e:
            # Re-raise exceptions from download/transcription as a ValueError
            raise ValueError(f"Failed to get transcript: {e}")
        finally:
            # Clean up the temporary audio files
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
            if sped_up_audio_path and os.path.exists(sped_up_audio_path):
                os.remove(sped_up_audio_path)