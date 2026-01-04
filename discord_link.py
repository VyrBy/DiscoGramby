import random, time
from db import get_db

async def start_link_process(ctx):
    print("start_link_process ЗАПУЩЕН")
    code = random.randint(100000, 999999)
    print(f"DEBUG: ctx={ctx}, author={ctx.author}, channel={ctx.channel}")

    db = get_db()
    c = db.cursor()

    try:
        c.execute(
            "INSERT INTO pending_links VALUES (?, ?, ?, ?, ?)",
            (code, ctx.author.id, ctx.guild.id, ctx.channel.id, int(time.time()))
        )
        db.commit()
        print("Строка успешно добавлена!")
    except Exception as e:
        print("ОШИБКА SQLITE:", e)

    db.close()

    print("Пытаюсь отправить сообщение...")

    await ctx.send(
        f"Ваш код подтверждения: **{code}**\n"
        f"Добавьте Telegram-бота в свою группу и напишите:\n"
        f"`/confirm {code}`"
    )

    print("Сообщение отправлено!")
