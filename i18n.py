import json
import os

_LOCALES = {}
DEFAULT_LANG = "en"

def load_locales():
    global _LOCALES
    for file in os.listdir("locales"):
        if file.endswith(".json"):
            lang = file[:-5]
            with open(f"locales/{file}", "r", encoding="utf-8") as f:
                _LOCALES[lang] = json.load(f)

def t(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    data = _LOCALES.get(lang, _LOCALES[DEFAULT_LANG])
    text = data.get(key, key)
    return text.format(**kwargs)
