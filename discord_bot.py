import discord
from discord.ext import commands
from discord_link import start_link_process
import json
from link_system.find_link import get_tg_target
from telegram_bot import tg_bot

with open("cfg.json", "r", encoding="utf-8") as f:
    config = json.load(f)

DISCORD_TOKEN = config["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
activity = discord.Game(name="Telegram")

discord_bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)


@discord_bot.event
async def on_ready():
    await discord_bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"{discord_bot.user} готов!")

@discord_bot.command(name="help")
async def help_commands(ctx):
    await ctx.send(
        f"Добро пожаловать на страницу помощи бота! Вот все существующие команды:\n"
        f"!link - начинает цикл привязки. Вы получите код, который будет необходимо ввести в телеграм чате\n"
        f"!unlink - отвязывает чаты друг от друга"
    )
    print("Отправлен раздел помощи")

# команда !link
@discord_bot.command(name="link")
async def link_cmd(ctx):
    print("Команда !link получена!")
    await start_link_process(ctx)

@discord_bot.command(name="unlink")
async def unlink_cmd(ctx):
    from db import get_db

    db = get_db()
    c = db.cursor()

    c.execute(
        "DELETE FROM linked_chats WHERE discord_channel_id=?",
        (ctx.channel.id,)
    )
    deleted = c.rowcount
    db.commit()
    db.close()

    if deleted > 0:
        await ctx.send("✅ Привязка к Telegram-группе была удалена.")
    else:
        await ctx.send("ℹ️ Этот канал не был привязан.")

@discord_bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Проверяем, есть ли связка для этого канала
    tg_chat_id = get_tg_target(message.channel.id)
    if tg_chat_id:
        # Формируем текст
        content = f"[{message.author.display_name}]:"
        if message.content:
            content += f"\n{message.content}"

        # Вложения
        if message.attachments:
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.jpg','jpeg','png','gif']):
                    await tg_bot.send_photo(chat_id=tg_chat_id, photo=attachment.url, caption=content)
                else:
                    await tg_bot.send_document(chat_id=tg_chat_id, document=attachment.url, caption=content)
        else:
            await tg_bot.send_message(chat_id=tg_chat_id, text=content)

    await discord_bot.process_commands(message)