import os
import logging
from flask import Blueprint, request, jsonify

upload_api = Blueprint('upload_api', __name__)
MERGED_UPLOAD_FOLDER = 'uploads/merged_srt'
os.makedirs(MERGED_UPLOAD_FOLDER, exist_ok=True)

# Setup logger for upload_api
logger = logging.getLogger("upload_api")
logger.setLevel(logging.INFO)
upload_handler = logging.FileHandler("logs/upload_api.log")
upload_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(upload_handler)

@upload_api.route('/upload_srt', methods=['POST'])
def upload_srt():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON data is required"}), 400

    token = request.headers.get('token')
    if not token:
        return jsonify({"error": "Token is required in headers"}), 400

    passcode = data.get('passcode')
    status = data.get('status')
    name_speakers = data.get('name_speakers')
    srt_text = data.get('srt_data')

    if not passcode:
        return jsonify({"error": "Passcode is required"}), 400
    if not srt_text:
        return jsonify({"error": "srt_data is required"}), 400
    if status not in ["guest", "user"]:
        return jsonify({"error": "Invalid status. Allowed values are 'guest' or 'user'"}), 400

    merged_file_name = os.path.join(MERGED_UPLOAD_FOLDER, f"{passcode}.srt")

    def parse_srt_text(srt_str):
        entries = []
        lines = srt_str.splitlines()
        i = 0
        while i < len(lines):
            if '-->' in lines[i]:
                parts = lines[i].split(' --> ')
                if len(parts) != 2:
                    i += 1
                    continue
                start_time = parts[0].strip()
                end_time = parts[1].strip()
                text = lines[i+1].strip() if (i+1) < len(lines) else ""
                entries.append((start_time, end_time, text))
                i += 2
            else:
                i += 1
        return entries

    new_entries = parse_srt_text(srt_text)
    all_entries = []
    if os.path.exists(merged_file_name):
        with open(merged_file_name, 'r', encoding='utf-8') as f:
            merged_content = f.read()
        all_entries = parse_srt_text(merged_content)

    existing_entries = set(all_entries)
    for entry in new_entries:
        if entry not in existing_entries:
            all_entries.append(entry)

    all_entries.sort(key=lambda x: x[0])
    with open(merged_file_name, 'w', encoding='utf-8') as merged_file:
        for entry in all_entries:
            merged_file.write(f"{entry[0]} --> {entry[1]}\n{entry[2]}\n\n")

    with open(merged_file_name, 'r', encoding='utf-8') as f:
        merged_content = f.read()

    response = {
        "passcode": passcode,
        "token": token,
        "status": status,
        "name_speakers": name_speakers,
        "merged_srt": merged_content
    }
    return jsonify(response), 200
