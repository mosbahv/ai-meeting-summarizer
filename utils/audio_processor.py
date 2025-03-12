import os
import io
import datetime
import srt
import torch
from pydub import AudioSegment
from tqdm import tqdm
from faster_whisper import WhisperModel

class AudioProcessor:
    def __init__(self, model_size="small"):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if torch.cuda.is_available() else "float32"
        print(f"Loading Whisper model on {device} with compute type {compute_type}...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def process_audio(self, audio_path, srt_file=None):
        """Convert audio to text and sync with SRT if available."""
        audio_buffer = self._convert_audio_to_wav(audio_path)
        print("Transcribing audio...")
        audio_segments = self._transcribe_audio(audio_buffer)
        if srt_file:
            print("Syncing with SRT file...")
            srt_segments = self._parse_srt(srt_file)
            merged_segments = self._merge_segments_with_srt(audio_segments, srt_segments)
        else:
            merged_segments = audio_segments
        return merged_segments

    def save_to_srt(self, segments, output_path):
        """Save merged texts to an SRT file."""
        print(f"Saving to SRT file: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(tqdm(segments, desc="Saving segments", unit="segment"), start=1):
                start = self._format_time(seg["start"])
                end = self._format_time(seg["end"])
                speaker = seg.get("speaker", "").strip()
                text = seg["text"].strip()
                if text:
                    f.write(f"{i}\n{start} --> {end}\n")
                    if speaker:
                        f.write(f"{speaker}: {text}\n\n")
                    else:
                        f.write(f"{text}\n\n")

    def _convert_audio_to_wav(self, audio_path):
        audio = AudioSegment.from_file(audio_path)
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)
        return wav_buffer

    def _transcribe_audio(self, audio_buffer):
        segments, _ = self.model.transcribe(audio_buffer, beam_size=1)
        return [
            {"start": seg.start, "end": seg.end, "text": seg.text}
            for seg in tqdm(segments, desc="Transcribing", unit="segment")
        ]

    def _parse_srt(self, srt_input):
        if isinstance(srt_input, (str, bytes, os.PathLike)):
            with open(srt_input, "r", encoding="utf-8") as f:
                srt_data = f.read()
        else:
            srt_input.seek(0)
            data = srt_input.read()
            srt_data = data.decode("utf-8") if isinstance(data, bytes) else data
        return list(srt.parse(srt_data))

    def _merge_segments_with_srt(self, audio_segments, srt_segments):
        merged_segments = []
        audio_index = 0
        total_audio = len(audio_segments)
        for srt_seg in tqdm(srt_segments, desc="Merging segments", unit="SRT segment"):
            collected_text = []
            srt_start_sec = srt_seg.start.total_seconds()
            srt_end_sec = srt_seg.end.total_seconds()
            while audio_index < total_audio and audio_segments[audio_index]["end"] <= srt_start_sec:
                audio_index += 1
            while audio_index < total_audio and audio_segments[audio_index]["start"] < srt_end_sec:
                collected_text.append(audio_segments[audio_index]["text"])
                audio_index += 1
            merged_text = " ".join(collected_text).strip()
            merged_segments.append({
                "start": srt_seg.start,
                "end": srt_seg.end,
                "speaker": srt_seg.content.strip() if srt_seg.content.strip() else "",
                "text": merged_text
            })
        return merged_segments

    def _format_time(self, seconds):
        if isinstance(seconds, datetime.timedelta):
            seconds = seconds.total_seconds()
        milliseconds = int((seconds % 1) * 1000)
        seconds = int(seconds)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
