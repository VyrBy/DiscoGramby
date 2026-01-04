from db import get_db

def get_discord_target(tg_chat_id):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT discord_guild_id, discord_channel_id FROM linked_chats WHERE telegram_chat_id = ?", (tg_chat_id,))
    row = c.fetchone()
    db.close()
    return row

def get_tg_target(discord_channel_id):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT telegram_chat_id FROM linked_chats WHERE discord_channel_id = ?", (discord_channel_id,))
    row = c.fetchone()
    db.close()
    return row[0] if row else None
