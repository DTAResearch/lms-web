# backend/app/services/i18n.py
from fastapi import Request
import json
import os
from typing import Dict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALE_DIR = os.path.join(BASE_DIR, "locales")

SUPPORTED_LANGUAGES = {"en", "vi"}

def load_translations(lang: str) -> Dict[str, str]:
    lang_dir = os.path.join(LOCALE_DIR, lang)
    if not os.path.exists(lang_dir):
        raise ValueError(f"Language directory for '{lang}' not found")

    translations = {}
    for filename in os.listdir(lang_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(lang_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                translations.update(data)
    return translations

def translate(key: str, lang: str = "en", **kwargs) -> str:
    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"
    translations = load_translations(lang)
    message = translations.get(key, key)
    return message.format(**kwargs) if kwargs else message

def get_request_language(request: Request, lang_from_path: str = None) -> str:
    # Ưu tiên ngôn ngữ từ đường dẫn nếu có, nếu không thì lấy từ header
    if lang_from_path and lang_from_path in SUPPORTED_LANGUAGES:
        return lang_from_path
    return request.headers.get("Accept-Language", "en").split(",")[0].split("-")[0]