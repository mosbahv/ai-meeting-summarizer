import os
import time
import io
from concurrent.futures import ThreadPoolExecutor
import datetime
from utils.audio_processor import AudioProcessor

AUDIO_FOLDER = "uploads/audio"
SRT_FOLDER = "uploads/merged_srt"
OUTPUT_DIR = "data"
LOGS_DIR = "logs"
PROCESSED_FILES_LOG = os.path.join(LOGS_DIR, "processed_files.log")
ERROR_LOG = os.path.join(LOGS_DIR, "errors.log")
PROCESSED_FILES = set()

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

if os.path.exists(PROCESSED_FILES_LOG):
    with open(PROCESSED_FILES_LOG, "r") as f:
        PROCESSED_FILES.update(f.read().splitlines())

audio_processor = AudioProcessor()

def log_error(message):
    """Log errors to a dedicated file in the logs folder."""
    with open(ERROR_LOG, "a") as error_log:
        error_log.write(f"{datetime.datetime.now()}: {message}\n")

def process_file(audio_path, srt_path, output_path):
    """Process an audio file and its corresponding SRT file."""
    try:
        with open(audio_path, "rb") as f_audio:
            audio_buffer = io.BytesIO(f_audio.read())
        srt_buffer = None
        if os.path.exists(srt_path):
            with open(srt_path, "rb") as f_srt:
                srt_buffer = io.BytesIO(f_srt.read())
        segments = audio_processor.process_audio(audio_buffer, srt_file=srt_buffer)
        audio_processor.save_to_srt(segments, output_path)
        print(f"File processed successfully: {audio_path}")
    except Exception as e:
        print(f"Error processing file {audio_path}: {e}")
        log_error(f"Error processing {audio_path}: {e}")

def monitor_and_process():
    print("Starting folder monitoring...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    while True:
        audio_files = [f for f in os.listdir(AUDIO_FOLDER) if f.endswith((".wav", ".mp3"))]
        with ThreadPoolExecutor() as executor:
            futures = []
            for audio_file in audio_files:
                output_path = os.path.join(OUTPUT_DIR, os.path.splitext(audio_file)[0] + ".srt")
                if audio_file not in PROCESSED_FILES and not os.path.exists(output_path):
                    audio_path = os.path.join(AUDIO_FOLDER, audio_file)
                    srt_path = os.path.join(SRT_FOLDER, os.path.splitext(audio_file)[0] + ".srt")
                    futures.append(executor.submit(process_file, audio_path, srt_path, output_path))
                    PROCESSED_FILES.add(audio_file)
                    with open(PROCESSED_FILES_LOG, "a") as f:
                        f.write(audio_file + "\n")
            for future in futures:
                future.result()
        time.sleep(1)
