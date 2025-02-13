import tiktoken
from openai import OpenAI

# تهيئة العميل لاستخدام deepseek-ai/deepseek-r1 عبر واجهة NVIDIA
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

def count_tokens(text):
    """
    دالة لحساب عدد التوكنات في النص باستخدام مكتبة tiktoken.
    """
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def split_text(text, max_tokens):
    """
    تقسيم النص إلى أجزاء بحيث لا يتجاوز كل جزء عدد التوكنات المحدد.
    """
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i+max_tokens]
        chunks.append(enc.decode(chunk_tokens))
    return chunks

def _generate_summary_chunk(text_chunk):
    """
    إنشاء ملخص جزئي للجزء المحدد من النص باستخدام deepseek.
    """
    prompt = (
        "قم بإنشاء ملخص جزئي يحتوي على:\n"
        "1. النقاط الرئيسية\n"
        "2. المهام الموكلة\n"
        "3. القرارات المتخذة\n"
        "4. الخطوات التالية\n\n"
        "التركيز على المعلومات الجديدة فقط:"
    )
    
    completion = client.chat.completions.create(
        model="deepseek-ai/deepseek-r1",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text_chunk}
        ],
        temperature=0.5,
        stream=False  # تأكد من تعطيل خاصية الستريم
    )
    
    return completion.choices[0].message.content

def _generate_final_summary(combined_summary):
    """
    دمج الملخصات الجزئية في تقرير نهائي متكامل.
    """
    prompt = (
        "قم بدمج الملخصات الجزئية التالية في تقرير واحد متكامل:\n"
        "- نظّم المحتوى بنفس الأقسام\n"
        "- احذف التكرار\n"
        "- رتّب المعلومات حسب الأهمية\n"
        "- حافظ على الإطار المهني"
    )
    
    completion = client.chat.completions.create(
        model="deepseek-ai/deepseek-r1",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": combined_summary}
        ],
        temperature=0.3,
        stream=False
    )
    
    return completion.choices[0].message.content

def generate_summary(transcription):
    """
    دالة رئيسية لإنشاء ملخص للاجتماع.
    - إذا كان النص قصيرًا (<= MAX_TOKENS) يتم معالجته مباشرة.
    - إذا كان النص طويلًا يتم تقسيمه إلى أجزاء، ثم دمج الملخصات الجزئية وإنشاء تقرير نهائي.
    """
    MAX_TOKENS = 6000

    if count_tokens(transcription) <= MAX_TOKENS:
        return _generate_summary_chunk(transcription)

    chunks = split_text(transcription, MAX_TOKENS)
    partial_summaries = [_generate_summary_chunk(chunk) for chunk in chunks]
    combined_summary = "\n\n".join(partial_summaries)

    return _generate_final_summary(combined_summary)
