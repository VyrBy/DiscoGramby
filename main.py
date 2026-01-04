import asyncio
from db import init_db
from telegram_bot import dp, tg_bot
from discord_bot import discord_bot, DISCORD_TOKEN

async def main():
    init_db()
    await tg_bot.delete_webhook(drop_pending_updates=True)

    # Запуск Telegram polling
    tg_task = dp.start_polling(tg_bot, skip_updates=True)

    # Запуск Discord бота
    discord_task = discord_bot.start(DISCORD_TOKEN)

    await asyncio.gather(tg_task, discord_task)

if __name__ == "__main__":
    asyncio.run(main())
