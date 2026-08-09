import os
import yt_dlp
from pydub import AudioSegment

AudioSegment.converter = r".\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffprobe = r".\ffmpeg\bin\ffprobe.exe"

os.makedirs('downloads', exist_ok=True)

def download_youtube_audio(url, output_path='downloads')->str:
    ydl_opts={
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        "ffmpeg_location": r"./ffmpeg/bin",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "192",
        }],
        "quiet": True   
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm",".wav").replace(".m4a",".wav")
    return filename
   

def stereo_to_mono(input_path: str) -> str:
    output_path: str = os.path.splitext(input_path)[0]+"_converted.wav"
    audio = AudioSegment.from_file(input_path)
    mono = audio.set_channels(1).set_frame_rate(16000)
    mono.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path:str,chunk_minutes:int=10)->list:
    audio = AudioSegment.from_wav(wav_path) 
    chunk_ms=chunk_minutes*60*1000
    chunks=[]
    for i , start in enumerate(range(0,len(audio),chunk_ms)):
        chunk=audio[start:start+chunk_ms]
        chunk_path= f"{os.path.splitext(wav_path)[0]}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks


def prepare_audio_chunks(url) -> list:
    download_path = download_youtube_audio(url, output_path="downloads")
    mono = stereo_to_mono(download_path)
    return chunk_audio(mono)


