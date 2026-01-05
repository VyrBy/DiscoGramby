import sqlite3
import os

DB_FILE = "links.db"

def get_db():
    print("Открываю базу:", os.path.abspath(DB_FILE))
    return sqlite3.connect(DB_FILE)

def init_db():
    db = get_db()
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS pending_links (
            code INTEGER PRIMARY KEY,
            discord_user_id INTEGER,
            discord_guild_id INTEGER,
            discord_channel_id INTEGER,
            created_at INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS linked_chats (
            discord_guild_id INTEGER,
            discord_channel_id INTEGER,
            telegram_chat_id INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_settings (
            platform TEXT,          -- "discord" | "telegram"
            chat_id INTEGER,
            language TEXT,
            PRIMARY KEY (platform, chat_id)
        )
    """)

    db.commit()
    db.close()
