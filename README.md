🎵 **Audio Processing & Report Generation Project** 🚀

This project is a **Flask**-based web application designed to process audio files, extract audio from video files, merge subtitle (SRT) files, and generate **professional AI-powered reports**. It utilizes powerful libraries such as **moviepy**, **requests**, **tiktoken**, **faster-whisper**, and more to deliver seamless functionality. 

---

## 🏗️ Project Structure

### 📁 **audio_api**: Audio Extraction from Video Files
- Downloads video files from **Cloudflare R2**.
- Extracts audio from videos using **moviepy** and converts it to WAV format.
- Logs all operations and errors for debugging.

### 📁 **summary_api**: Professional Report Generation
- Extracts text from **SRT subtitle files**.
- Uses **AI-powered** `ProfessionalReportGenerator` to create structured JSON reports.
- Saves reports in the `reports/` folder and raw data in `data/`.

### 📁 **upload_api**: Subtitle Upload & Merging
- Accepts subtitle (SRT) data via JSON payload.
- Merges new SRT data with existing files and saves them in `uploads/merged_srt/`.

### 🛠️ **AudioProcessor**: Advanced Audio Handling
- Converts audio files to WAV format using **pydub**.
- Transcribes audio using **faster-whisper** (optimized for speed and accuracy).
- Synchronizes transcriptions with subtitle timestamps and saves as **SRT** files.

### ⚙️ **Background Tasks**
- Monitors `uploads/audio` and `uploads/srt` for new files.
- Automatically processes new files using **ThreadPoolExecutor & threading**.

---

## 📌 **Requirements**

🔹 **Python 3.8+**
🔹 Required Python libraries:
```bash
Flask
requests
moviepy
tiktoken
openai  # or a compatible API client
pydub
torch
faster-whisper
tqdm
srt
dotenv
```
💡 Install dependencies using:
```bash
pip install -r requirements.txt
```

🚀 **Ready to revolutionize audio processing and reporting? Let’s build!** 🎤✨
