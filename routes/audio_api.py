import os
import logging
import requests
from flask import Blueprint, request, jsonify, send_file
from tempfile import NamedTemporaryFile
from moviepy import VideoFileClip

audio_api = Blueprint('audio_api', __name__)

CLOUDFLARE_VIDEO_URL = "https://bucket-name.r2.cloudflarestorage.com/"
UPLOAD_FOLDER = "uploads/audio"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup logger for audio_api
logger = logging.getLogger("audio_api")
logger.setLevel(logging.INFO)
audio_handler = logging.FileHandler("logs/audio_api.log")
audio_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(audio_handler)

@audio_api.route('/extract_audio', methods=['GET'])
def extract_audio():
    video_name = request.args.get('video')
    if not video_name:
        logger.error("Video file name is required but missing.")
        return jsonify({"error": "Video file name is required"}), 400

    video_url = f"{CLOUDFLARE_VIDEO_URL}{video_name}"
    logger.info(f"Fetching video from: {video_url}")
    try:
        with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            response = requests.get(video_url, stream=True)
            if response.status_code != 200:
                logger.error(f"Failed to download video. Status Code: {response.status_code}")
                return jsonify({"error": "Failed to download video"}), 500

            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    temp_video.write(chunk)
            temp_video_path = temp_video.name
            logger.info(f"Video downloaded successfully: {temp_video_path}")

        # Extract audio and save to UPLOAD_FOLDER
        audio_filename = f"{os.path.splitext(video_name)[0]}.wav"
        audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
        with VideoFileClip(temp_video_path) as video_clip:
            video_clip.audio.write_audiofile(audio_path, codec='pcm_s16le')
        logger.info(f"Audio extracted successfully: {audio_path}")

        os.remove(temp_video_path)
        return send_file(audio_path, as_attachment=True)

    except Exception as e:
        logger.exception("Error extracting audio")
        return jsonify({"error": str(e)}), 500
