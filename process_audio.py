from faster_whisper import WhisperModel
from pydub import AudioSegment
import torch
from io import BytesIO

device = "cpu" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "float32"
model = WhisperModel("small", device=device, compute_type=compute_type)

def transcribe_audio(file_path, chunk_size=10):
    audio = AudioSegment.from_file(file_path)
    chunk_length_ms = chunk_size * 60 * 1000
    chunks = make_chunks(audio, chunk_length_ms)

    full_transcription = ""
    for chunk in chunks:
        with BytesIO() as buffer:
            chunk.export(buffer, format="wav")
            buffer.seek(0)
            segments, _ = model.transcribe(
                buffer,
                beam_size=5,
                vad_filter=True,
                word_timestamps=False
            )
            chunk_text = "\n".join([segment.text for segment in segments])
            full_transcription += chunk_text + "\n"

    return full_transcription

def make_chunks(audio, chunk_size):
    return [audio[i:i+chunk_size] for i in range(0, len(audio), chunk_size)]
