from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot import dp, bot
import sqlite3
from datetime import datetime

conn = sqlite3.connect("giftelf.db")
conn.execute("""CREATE TABLE IF NOT EXISTS deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller INTEGER,
    buyer INTEGER,
    status TEXT,
    desc TEXT,
    created_at TEXT,
    updated_at TEXT
)""")
conn.commit()

@dp.message_handler(commands=["create"])
async def create_deal(message: types.Message):
    desc = message.get_args()
    if not desc:
        return await message.reply("Опиши, что ты хочешь подарить. Пример: /create Носки и шоколад")
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("INSERT INTO deals(seller, buyer, status, desc, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
              (message.from_user.id, None, "open", desc, now, now))
    conn.commit()
    deal_id = c.lastrowid
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("🎁 Принять подарок", callback_data=f"accept|{deal_id}"))
    await message.answer(f"🎉 Сделка #{deal_id} создана: {desc}", reply_markup=kb)

@dp.message_handler(commands=["list"])
async def list_deals(message: types.Message):
    c = conn.cursor()
    c.execute("SELECT id, desc FROM deals WHERE status='open'")
    rows = c.fetchall()
    if not rows:
        return await message.answer("Нет доступных подарков.")
    text = "\n".join([f"#{r[0]} — {r[1]}" for r in rows])
    await message.answer("🎁 Доступные подарки:\n" + text)

@dp.callback_query_handler(lambda c: c.data.startswith("accept|"))
async def accept_deal(callback: types.CallbackQuery):
    deal_id = int(callback.data.split("|")[1])
    c = conn.cursor()
    c.execute("SELECT seller, status FROM deals WHERE id=?", (deal_id,))
    row = c.fetchone()
    if not row or row[1] != "open":
        return await callback.answer("Сделка уже недоступна.")
    now = datetime.now().isoformat()
    c.execute("UPDATE deals SET buyer=?, status=?, updated_at=? WHERE id=?",
              (callback.from_user.id, "ongoing", now, deal_id))
    conn.commit()
    await bot.send_message(row[0], f"🎁 Ваш подарок принят пользователем @{callback.from_user.username or callback.from_user.id}")
    await callback.message.edit_text("Ты принял участие в сделке!")
    await callback.answer("Сделка принята!")
