from db import get_db

DEFAULT_LANG = "en"

def get_lang(platform: str, chat_id: int) -> str:
    db = get_db()
    c = db.cursor()

    c.execute(
        "SELECT language FROM chat_settings WHERE platform=? AND chat_id=?",
        (platform, chat_id)
    )
    row = c.fetchone()
    db.close()

    return row[0] if row else DEFAULT_LANG


def set_lang(platform: str, chat_id: int, lang: str):
    db = get_db()
    c = db.cursor()

    c.execute("""
        INSERT INTO chat_settings (platform, chat_id, language)
        VALUES (?, ?, ?)
        ON CONFLICT(platform, chat_id)
        DO UPDATE SET language=excluded.language
    """, (platform, chat_id, lang))

    db.commit()
    db.close()
