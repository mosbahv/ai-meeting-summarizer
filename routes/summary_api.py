import os
import json
import logging
from flask import Blueprint, request, jsonify
from utils.summary_generator import ProfessionalReportGenerator

summary_api = Blueprint('summary_api', __name__)
report_generator = ProfessionalReportGenerator()

REPORTS_FOLDER = 'reports'
DATA_FOLDER = 'data'
os.makedirs(REPORTS_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# إعداد اللوجر
logger = logging.getLogger("summary_api")
logger.setLevel(logging.INFO)
summary_handler = logging.FileHandler("logs/summary_api.log")
summary_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(summary_handler)

def extract_text_from_srt(srt_file_path):
    """استخراج النص من ملف SRT."""
    try:
        with open(srt_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        text = " ".join([line.strip() for line in lines if not line.strip().isdigit() and '-->' not in line])
        return text.strip()
    except Exception as e:
        logger.error(f"خطأ أثناء استخراج النص من ملف SRT: {e}")
        raise

def generate_and_save_report(passcode):
    """توليد وحفظ التقرير في مجلد التقارير."""
    data_file_path = os.path.join(DATA_FOLDER, f"{passcode}.srt")

    if not os.path.exists(data_file_path):
        logger.warning(f"ملف البيانات غير موجود: {data_file_path}")
        return {"error": f"Data file for passcode {passcode} not found"}, 404

    try:
        text_data = extract_text_from_srt(data_file_path)
        report = report_generator.generate_report(text_data)

        if not report:
            logger.error("فشل في توليد التقرير")
            return {"error": "Failed to generate report"}, 500

        report_file_path = os.path.join(REPORTS_FOLDER, f"{passcode}.json")

        # حفظ التقرير الجديد باسم فريد إذا كان هناك تقرير سابق
        index = 1
        while os.path.exists(report_file_path):
            report_file_path = os.path.join(REPORTS_FOLDER, f"{passcode}_{index}.json")
            index += 1

        with open(report_file_path, 'w', encoding='utf-8') as file:
            json.dump(report, file, indent=4, ensure_ascii=False)

        logger.info(f"تم إنشاء التقرير بنجاح: {report_file_path}")
        return {"report": report, "file": report_file_path}, 200
    except Exception as e:
        logger.error(f"خطأ أثناء توليد التقرير: {e}")
        return {"error": str(e)}, 500

@summary_api.route('/generate_report', methods=['POST'])
def generate_report():
    """نقطة النهاية لإنشاء التقرير."""
    data = request.get_json()
    passcode = data.get('passcode')
    force_new = data.get('force', False)  # التحكم في إنشاء تقرير جديد حتى لو كان موجودًا

    if not passcode:
        return jsonify({"error": "Passcode is required"}), 400

    report_file_path = os.path.join(REPORTS_FOLDER, f"{passcode}.json")

    # إذا كان `force_new = False` وهناك تقرير موجود، قم بإرجاعه مباشرة
    if os.path.exists(report_file_path) and not force_new:
        with open(report_file_path, 'r', encoding='utf-8') as file:
            report_data = json.load(file)
        return jsonify({"report": report_data}), 200

    # توليد تقرير جديد
    return jsonify(generate_and_save_report(passcode)[0]), 200
