from aiogram import Bot, Dispatcher
from aiogram import Router, F
from aiogram.types import Message, ChatMemberAdministrator, ChatMemberOwner
from aiogram.filters import Command
from link_system.find_link import get_discord_target
from link_system.telegram_confirm import confirm_code
from db import get_db
from lang_store import set_lang, get_lang
from i18n import t
import json

with open("cfg.json", "r", encoding="utf-8") as f:
    config = json.load(f)

TELEGRAM_TOKEN = config["TELEGRAM_TOKEN"]

tg_bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
router = Router()


def is_admin(status):
    return isinstance(status, (ChatMemberAdministrator, ChatMemberOwner))

@router.message(Command("lang"))
async def set_lang_cmd(message: Message):
    parts = message.text.split()
    if len(parts) != 2:
        await message.reply("Usage: /lang <ru|en>")
        return

    lang = parts[1].lower()
    if lang not in ("ru", "en"):
        await message.reply("Available languages: ru, en")
        return

    set_lang("telegram", message.chat.id, lang)
    await message.reply(f"🌍 Language set to {lang}")


@router.message(F.text == "/unlink")
async def unlink_cmd(message: Message):
    # Проверяем, что пользователь — администратор
    member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    lang = get_lang("telegram", message.chat.id)

    if not is_admin(member):
        await message.reply(t('message.error', lang))
        return

    db = get_db()
    c = db.cursor()

    # Удаляем связи по telegram_chat_id
    c.execute("DELETE FROM linked_chats WHERE telegram_chat_id=?", (message.chat.id,))
    deleted = c.rowcount
    db.commit()
    db.close()

    if deleted > 0:
        await message.reply(t('unlinked.success', lang))
    else:
        await message.reply(t('unlink.none', lang))

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
    lang = get_lang("telegram", message.chat.id)

    guild_id, channel_id = target
    # discord_channel нужно получить из discord_bot
    from discord_bot import discord_bot
    discord_channel = discord_bot.get_channel(channel_id)
    if not discord_channel:
        return

    author = message.from_user.first_name
    tg_link = message.get_url()

    if tg_link:
        content = f"[[{author}]({tg_link})]:"
    else:
        content = f"[{author}]:"

    if message.text:
        await discord_channel.send(f"{content}\n{message.text}")

    # Фото
    if message.photo:
        photo = message.photo[-1]
        file = await tg_bot.get_file(photo.file_id)
        file_url = content + f"\n[{t('photo', lang)}](https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file.file_path})"
        await discord_channel.send(file_url)

    # Документы и файлы
    if message.document:
        file = await tg_bot.get_file(message.document.file_id)
        file_url = content + f"\n[{t('file', lang)}](https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file.file_path})"
        await discord_channel.send(file_url)

    # Видео
    if message.video:
        file = await tg_bot.get_file(message.video.file_id)
        file_url = content + f"\n[{t('video', lang)}](https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file.file_path})"
        await discord_channel.send(file_url)

    # Стикеры
    if message.sticker:
        file = await tg_bot.get_file(message.sticker.file_id)
        file_url = content + f"\n[{t('sticker', lang)}](https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file.file_path})"
        await discord_channel.send(file_url)