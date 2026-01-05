import random, time
from db import get_db
from i18n import t
from lang_store import get_lang

async def start_link_process(ctx):
    print("start_link_process ЗАПУЩЕН")
    code = random.randint(100000, 999999)
    print(f"DEBUG: ctx={ctx}, author={ctx.author}, channel={ctx.channel}")
    lang = get_lang("discord", ctx.guild.id)

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

        ctx.send(f"{t('command.error'+f"\n{e}", lang)}")
        print("ОШИБКА SQLITE:", e)

    db.close()

    print("Пытаюсь отправить сообщение...")

    await ctx.send(
        f"{t('link.code', lang, code=code)}\n"
        f"{t('link.instruction', lang, code=code)}"
    )

    print("Сообщение отправлено!")
