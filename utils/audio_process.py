import os
import shutil
import tempfile
import yt_dlp
from pydub import AudioSegment

# Added this because so that auto detect FFmpeg on any OS 
AudioSegment.converter = shutil.which("ffmpeg")
AudioSegment.ffprobe = shutil.which("ffprobe")

# Use a temp directory for downloads 
DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), "audio")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url, output_path=None) -> str:
    if output_path is None:
        output_path = DOWNLOAD_DIR

    ffmpeg_path = shutil.which("ffmpeg")
    ffmpeg_dir = os.path.dirname(ffmpeg_path) if ffmpeg_path else ""

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        "ffmpeg_location": ffmpeg_dir,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "192",
        }],
        "quiet": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
    return filename


def stereo_to_mono(input_path: str) -> str:
    output_path: str = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    mono = audio.set_channels(1).set_frame_rate(16000)
    mono.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]
        chunk_path = f"{os.path.splitext(wav_path)[0]}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks


def cleanup_files(file_paths: list):
    """Delete temporary audio files after processing."""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass


def prepare_audio_chunks(url) -> list:
    download_path = download_youtube_audio(url)
    mono = stereo_to_mono(download_path)
    chunks = chunk_audio(mono)
    # Clean up intermediate files (original download + mono conversion)
    cleanup_files([download_path, mono])
    return chunks
