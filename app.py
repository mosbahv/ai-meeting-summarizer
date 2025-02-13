from flask import Flask, render_template, request, jsonify
from fetch_from_cloud import fetch_file
from process_audio import transcribe_audio
from report_generator import generate_summary
import os

app = Flask(__name__)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio_file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    audio_file = request.files['audio_file']
    if audio_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(OUTPUT_DIR, audio_file.filename)
    audio_file.save(file_path)

    try:
        transcription = transcribe_audio(file_path)
        summary = generate_summary(transcription)
        print ("summary: ", summary)
        return jsonify({
            "transcription": transcription,
            "summary": summary
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/fetch_from_cloud', methods=['POST'])
def fetch_from_cloud_endpoint():
    try:
        file_path = fetch_file()
        transcription = transcribe_audio(file_path)
        summary = generate_summary(transcription)
        return jsonify({
            "transcription": transcription,
            "summary": summary
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    