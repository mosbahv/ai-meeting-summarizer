from flask import Flask
from dotenv import load_dotenv
import logging
import threading
from routes.audio_api import audio_api
from routes.summary_api import summary_api
from routes.upload_api import upload_api
from utils.auto_AudioProcessor import monitor_and_process

load_dotenv()

# Setup logger for the main application
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = Flask(__name__)
app.register_blueprint(audio_api)
app.register_blueprint(summary_api)
app.register_blueprint(upload_api)

def start_background_tasks():
    """Start background tasks using threading."""
    try:
        thread = threading.Thread(target=monitor_and_process, daemon=True)
        thread.start()
    except Exception as e:
        logger.error(f"Error starting background tasks: {e}")

if __name__ == "__main__":
    start_background_tasks()
    print(app.url_map)
    app.run(debug=False,host="0.0.0.0",port=5000)
            
