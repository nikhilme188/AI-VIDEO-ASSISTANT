import os
from groq import Groq
from dotenv import load_dotenv
from utils.audio_process import prepare_audio_chunks
load_dotenv()



client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def speech_to_text(chunk_paths: list) -> str:
    """Transcribe a list of WAV audio chunks using Groq Whisper"""

    transcript = []

    for i, chunk_path in enumerate(chunk_paths, start=1):

        print(f"Processing Chunk {i}: {chunk_path}")

        with open(chunk_path, "rb") as audio_file:

            response = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=audio_file,
                response_format="text",
                temperature=0
            )

        print(f"Chunk {i} Completed")

        transcript.append(response)

    return "\n".join(transcript)


