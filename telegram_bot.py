from aiogram import Bot, Dispatcher
from aiogram import Router, F
from aiogram.types import Message, ChatMemberAdministrator, ChatMemberOwner
from aiogram.filters import Command
from link_system.find_link import get_discord_target
from link_system.telegram_confirm import confirm_code
import json
from db import get_db


with open("cfg.json", "r", encoding="utf-8") as f:
    config = json.load(f)

TELEGRAM_TOKEN = config["TELEGRAM_TOKEN"]

tg_bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
router = Router()

def is_admin(status):
    return isinstance(status, (ChatMemberAdministrator, ChatMemberOwner))

@router.message(F.text == "/unlink")
async def unlink_cmd(message: Message):
    # Проверяем, что пользователь — администратор
    member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    if not is_admin(member):
        await message.reply("❌ Эту команду могут использовать только администраторы группы.")
        return

    db = get_db()
    c = db.cursor()

    # Удаляем связи по telegram_chat_id
    c.execute("DELETE FROM linked_chats WHERE telegram_chat_id=?", (message.chat.id,))
    deleted = c.rowcount
    db.commit()
    db.close()

    if deleted > 0:
        await message.reply("✅ Эта Telegram-группа успешно отвязана от Discord.")
    else:
        await message.reply("ℹ️ Эта группа не была привязана.")

# Команда /confirm
@dp.message(Command(commands=["confirm"]))
async def cmd_confirm(message: Message):
    await confirm_code(message, tg_bot)

# Пересылка сообщений из Telegram → Discord
@dp.message()
async def tg_to_discord(message: Message):
    target = get_discord_target(message.chat.id)
    if not target:
        return  # связь не настроена

    guild_id, channel_id = target
    # discord_channel нужно получить из discord_bot
    from discord_bot import discord_bot
    discord_channel = discord_bot.get_channel(channel_id)
    if not discord_channel:
        return

    author = message.from_user.first_name
    tg_link = f"https://t.me/{message.chat.username}/{message.message_id}"
    content = f"[[{author}]({tg_link})]:"

    if message.text:
        content += f"\n{message.text}"

    # Сначала отправим текст (если есть)
    if message.text:
        await discord_channel.send(content)

    # Фото
    if message.photo:
        photo = message.photo[-1]
        file = await tg_bot.get_file(photo.file_id)
        file_url = content + f"\n[Изображение](https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file.file_path})"
        await discord_channel.send(file_url)

    # Документы и файлы
    if message.document:
        file = await tg_bot.get_file(message.document.file_id)
        file_url = content + f"\n[Файл](https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file.file_path})"
        await discord_channel.send(file_url)

    # Видео
    if message.video:
        file = await tg_bot.get_file(message.video.file_id)
        file_url = content + f"\n[Видео](https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file.file_path})"
        await discord_channel.send(file_url)

    # Стикеры
    if message.sticker:
        file = await tg_bot.get_file(message.sticker.file_id)
        file_url = content + f"\n[Стикер](https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file.file_path})"
        await discord_channel.send(file_url)