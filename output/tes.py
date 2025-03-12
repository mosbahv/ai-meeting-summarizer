import re
from collections import defaultdict
from datetime import timedelta

# دالة لتحليل ملف SRT
def parse_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # نمط لاستخراج المعلومات من ملف SRT
    pattern = r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?):\s(.+)"
    matches = re.findall(pattern, content)

    data = []
    for match in matches:
        start_time, end_time, speaker, text = match[1], match[2], match[3], match[4]
        data.append({
            "start_time": start_time,
            "end_time": end_time,
            "speaker": speaker,
            "text": text
        })
    return data

# دالة لتحويل الطابع الزمني إلى ثوانٍ
def time_to_seconds(timestamp):
    h, m, s_ms = timestamp.split(':')
    s, ms = s_ms.split(',')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

# دالة لحساب مدة الحديث لكل متحدث
def calculate_durations(data):
    durations = defaultdict(timedelta)  # استخدام timedelta لحساب المدة الزمنية
    for entry in data:
        start = time_to_seconds(entry["start_time"])
        end = time_to_seconds(entry["end_time"])
        duration = end - start
        durations[entry["speaker"]] += timedelta(seconds=duration)
    return {speaker: duration.total_seconds() for speaker, duration in durations.items()}

# دالة لإنشاء التقرير
def generate_report(data, durations):
    report = "تقرير الاجتماع الشامل\n\n"

    # قسم المشاركين
    report += "### المشاركون:\n"
    for speaker, duration in durations.items():
        minutes, seconds = divmod(duration, 60)
        report += f"- {speaker}: {int(minutes)} دقيقة و {int(seconds)} ثانية\n"

    # قسم النصوص المختارة
    report += "\n### نصوص مختارة:\n"
    for entry in data[:10]:  # عرض أول 10 نصوص فقط
        report += f"{entry['start_time']} - {entry['end_time']} | {entry['speaker']}: {entry['text']}\n"

    return report

# تنفيذ التحليل
file_path = r"D:\Teknoverse\ai meeting summarizer v2\output\117_processed.srt"  # استبدل بالمسار الفعلي لملف SRT
srt_data = parse_srt(file_path)
durations = calculate_durations(srt_data)
report = generate_report(srt_data, durations)

# حفظ التقرير
with open("meeting_report.txt", "w", encoding="utf-8") as file:
    file.write(report)

print("تم إنشاء التقرير بنجاح!")
