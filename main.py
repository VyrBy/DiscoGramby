import asyncio
import sys
from db import init_db
from telegram_bot import dp, tg_bot
from discord_bot import discord_bot, DISCORD_TOKEN
from i18n import load_locales
load_locales()



async def console_listener(shutdown_event: asyncio.Event):
    print("Введите 'stop' для остановки бота")

    while not shutdown_event.is_set():
        cmd = await asyncio.to_thread(input)

        if cmd.strip().lower() in ("stop", "exit", "quit"):
            print("Останавливаю бота...")
            shutdown_event.set()


async def shutdown():
    print("Завершение сервисов...")

    # Остановка Telegram
    await dp.stop_polling()
    await tg_bot.session.close()

    # Остановка Discord
    await discord_bot.close()

    print("Бот успешно остановлен.")


async def main():
    init_db()
    await tg_bot.delete_webhook(drop_pending_updates=True)

    shutdown_event = asyncio.Event()

    tg_task = asyncio.create_task(
        dp.start_polling(tg_bot, skip_updates=True)
    )

    discord_task = asyncio.create_task(
        discord_bot.start(DISCORD_TOKEN)
    )

    console_task = asyncio.create_task(
        console_listener(shutdown_event)
    )

    # Ждём сигнал остановки
    await shutdown_event.wait()

    # Корректно завершаем
    await shutdown()

    # Отменяем таски
    for task in (tg_task, discord_task, console_task):
        task.cancel()

    await asyncio.gather(
        tg_task, discord_task, console_task,
        return_exceptions=True
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Остановлено через Ctrl+C")
