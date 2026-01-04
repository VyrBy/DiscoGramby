from db import get_db
import time
from aiogram.types import Message

EXPIRATION_TIME = 300

async def confirm_code(message: Message, bot):
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Использование: /confirm <код>")
        return

    code = int(parts[1])

    db = get_db()
    c = db.cursor()

    # 🔥 Удаляем все устаревшие заявки
    cutoff = int(time.time()) - EXPIRATION_TIME
    c.execute("DELETE FROM pending_links WHERE created_at < ?", (cutoff,))
    db.commit()


    # Проверяем, существует ли код
    c.execute(
        "SELECT discord_user_id, discord_guild_id, discord_channel_id, created_at FROM pending_links WHERE code = ?", (code,)
    )
    row = c.fetchone()

    if not row:
        await message.answer("❌ Неверный или устаревший код!")
        return

    discord_user_id, guild_id, channel_id, created_at = row


    # Проверка, что пользователь — админ группы
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ["administrator", "creator"]:
        await message.answer("❌ Вы должны быть администратором группы!")
        return

    # Создаём связку
    c.execute("INSERT INTO linked_chats VALUES (?, ?, ?)", (guild_id, channel_id, message.chat.id))
    c.execute("DELETE FROM pending_links WHERE code= ? ", (code,))

    db.commit()
    db.close()

    await message.answer("✅ Группа успешно подключена к Discord!")
