# import tiktoken
# import json
# import re
# from openai import OpenAI
# import os
# from dotenv import load_dotenv
# load_dotenv(".env")

# class ProfessionalReportGenerator:
#     def __init__(self):
#         self.client = OpenAI(
#             base_url=os.getenv("API_BASE_URL"),
#             api_key=os.getenv("API_KEY")
#         )
#         self.enc = tiktoken.get_encoding("cl100k_base")

#     def generate_report(self, text):
#         print("im start in generate_report ")
#         """الدالة الرئيسية لإنشاء التقرير"""
#         if self._count_tokens(text) <= 6000:
#             return self._generate_chunk_report(text)
#         return self._generate_hierarchical_report(text)

#     def _count_tokens(self, text):
#         return len(self.enc.encode(text))

#     def _split_text(self, text, max_tokens=6000):
#         tokens = self.enc.encode(text)
#         return [self.enc.decode(tokens[i:i+max_tokens])
#                 for i in range(0, len(tokens), max_tokens)]

#     def _extract_json(self, raw_text):
#         print("im in _extract_json")
#         """
#         دالة لاستخراج محتوى JSON من النص.
#         تبحث عن الكود المحصور بين ```json و ``` وتعيده.
#         """
#         match = re.search(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL)
#         if match:
#             json_text = match.group(1)
#             try:
#                 return json.loads(json_text)
#             except json.JSONDecodeError as e:
#                 print(f"❌ خطأ في تحويل JSON: {e}")
#                 print("المحتوى المستلم:", json_text)
#                 return None
#         else:
#             print("❌ لم يتم العثور على JSON في الاستجابة!")
#             print("المحتوى المستلم:", raw_text)
#             return None

#     def _generate_chunk_report(self, chunk):
#         print("im in _generate_chunk_report")
#         # قالب JSON ثابت للتقرير
#         json_template = {
#             "summary": "",
#             "participants_analysis": {
#                 "total_speakers": 0,
#                 "top_speakers": [],
#                 "avg_speaking_time": 0.0
#             },
#             "key_questions_answers": [
#                 {"question": "", "answer": ""}
#             ],
#             "main_topics": [],
#             "general_notes": [],
#             "future_recommendations": []
#         }
        
#         prompt = f"""أنشئ تقريرًا شاملًا ومهنيًا من النص التالي على شكل JSON وفق النموذج التالي دون تغيير البنية:
# ```json
# {json.dumps(json_template, indent=4, ensure_ascii=False)}
# ```
# النص:
# {chunk}
# """
#         response = self.client.chat.completions.create(
#             model="deepseek-ai/deepseek-r1",
#             messages=[
#                 {"role": "system", "content": prompt},
#                 {"role": "user", "content": chunk}
#             ],
#             temperature=0.5
#         )
        
#         raw_response = response.choices[0].message.content
#         return self._extract_json(raw_response)

#     def _generate_hierarchical_report(self, text):
#         """تجزئة النصوص الطويلة وتجميعها في تقرير نهائي"""
#         chunks = self._split_text(text)
#         partial_reports = [self._generate_chunk_report(c) for c in chunks]
        
#         # تحويل التقارير الجزئية إلى نص JSON لاستخدامه في الـ prompt
#         combined = json.dumps(partial_reports, indent=4, ensure_ascii=False)
        
#         merge_prompt = f"""ادمج التقارير الجزئية التالية في تقرير نهائي بنفس بنية JSON التالية:
# - احذف التكرار.
# - رتب المعلومات حسب الأهمية.
# - حافظ على الهيكل الاحترافي المذكور.
# ```json
# {json.dumps(partial_reports[0], indent=4, ensure_ascii=False)}
# ```"""
        
#         final_response = self.client.chat.completions.create(
#             model="deepseek-ai/deepseek-r1",
#             messages=[
#                 {"role": "system", "content": merge_prompt},
#                 {"role": "user", "content": combined}
#             ],
#             temperature=0.3
#         )
        
#         raw_final_response = final_response.choices[0].message.content
#         return self._extract_json(raw_final_response)import tiktoken
import json
import re
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import tiktoken

load_dotenv(".env")

class ProfessionalReportGenerator:
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("API_BASE_URL"),
            api_key=os.getenv("API_KEY")
        )
        self.enc = tiktoken.get_encoding("cl100k_base")

    def generate_report(self, text):
        print("Starting generate_report method")
        """Main function to generate the report"""
        if self._count_tokens(text) <= 6000:
            return self._generate_chunk_report(text)
        return self._generate_hierarchical_report(text)

    def _count_tokens(self, text):
        return len(self.enc.encode(text))

    def _split_text(self, text, max_tokens=6000):
        tokens = self.enc.encode(text)
        return [self.enc.decode(tokens[i:i+max_tokens])
                for i in range(0, len(tokens), max_tokens)]

    def _extract_json(self, raw_text):
        print("Inside _extract_json method")
        """
        Function to extract JSON content from the text.
        Searches for code enclosed between ```json and ``` and returns it.
        """
        match = re.search(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL)
        if match:
            json_text = match.group(1)
            try:
                return json.loads(json_text)
            except json.JSONDecodeError as e:
                print(f"❌ JSON decoding error: {e}")
                print("Received content:", json_text)
                return None
        else:
            print("❌ No JSON found in the response!")
            print("Received content:", raw_text)
            return None

    def _generate_chunk_report(self, chunk):
        print("Inside _generate_chunk_report method")
        # Fixed JSON template for the report
        json_template = {
            "summary": "",
            "participants_analysis": {
                "total_speakers": 0,
                "top_speakers": [],
                "avg_speaking_time": 0.0
            },
            "key_questions_answers": [
                {"question": "", "answer": ""}
            ],
            "main_topics": [],
            "general_notes": [],
            "future_recommendations": []
        }
        
        prompt = f"""Generate a comprehensive and professional report from the following text in JSON format following this structure exactly:
```json
{json.dumps(json_template, indent=4, ensure_ascii=False)}
```
Text:
{chunk}
"""
        
        response = self.client.chat.completions.create(
            model="deepseek-ai/deepseek-r1",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": chunk}
            ],
            temperature=0.5
        )
        
        raw_response = response.choices[0].message.content
        return self._extract_json(raw_response)

    def _generate_hierarchical_report(self, text):
        """Splitting long texts and aggregating them into a final report"""
        chunks = self._split_text(text)
        partial_reports = [self._generate_chunk_report(c) for c in chunks]
        
        # Convert partial reports into JSON for prompt usage
        combined = json.dumps(partial_reports, indent=4, ensure_ascii=False)
        
        merge_prompt = f"""Merge the following partial reports into a final structured JSON report:
- Remove duplicates.
- Arrange information by importance.
- Maintain the professional structure provided.
```json
{json.dumps(partial_reports[0], indent=4, ensure_ascii=False)}
```
"""
        
        final_response = self.client.chat.completions.create(
            model="deepseek-ai/deepseek-r1",
            messages=[
                {"role": "system", "content": merge_prompt},
                {"role": "user", "content": combined}
            ],
            temperature=0.3
        )
        
        raw_final_response = final_response.choices[0].message.content
        return self._extract_json(raw_final_response)

