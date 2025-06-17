from aiogram import types
from bot import dp
import sqlite3
from datetime import datetime

conn = sqlite3.connect("giftelf.db")

@dp.message_handler(commands=["mydeals"])
async def my_deals(message: types.Message):
    uid = message.from_user.id
    c = conn.cursor()
    c.execute("SELECT id, desc, status FROM deals WHERE seller=? OR buyer=?", (uid, uid))
    rows = c.fetchall()
    if not rows:
        return await message.answer("У тебя пока нет сделок.")
    text = "\n".join([f"#{r[0]} — {r[1]} [{r[2]}]" for r in rows])
    await message.answer("🗂 Твои сделки:\n" + text)

@dp.message_handler(commands=["cancel"])
async def cancel_deal(message: types.Message):
    args = message.get_args()
    if not args or not args.isdigit():
        return await message.reply("Пример: /cancel 2")
    deal_id = int(args)
    c = conn.cursor()
    c.execute("SELECT seller, status FROM deals WHERE id=?", (deal_id,))
    row = c.fetchone()
    if not row or row[0] != message.from_user.id:
        return await message.reply("Ты не можешь отменить эту сделку.")
    if row[1] != "open":
        return await message.reply("Сделка уже принята, её нельзя отменить.")
    now = datetime.now().isoformat()
    c.execute("UPDATE deals SET status=?, updated_at=? WHERE id=?", ("cancelled", now, deal_id))
    conn.commit()
    await message.answer(f"Сделка #{deal_id} отменена.")

@dp.message_handler(commands=["finish"])
async def finish_deal(message: types.Message):
    args = message.get_args()
    if not args or not args.isdigit():
        return await message.reply("Пример: /finish 3")
    deal_id = int(args)
    c = conn.cursor()
    c.execute("SELECT seller, buyer, status FROM deals WHERE id=?", (deal_id,))
    row = c.fetchone()
    if not row or row[0] != message.from_user.id:
        return await message.reply("Ты не создатель этой сделки.")
    if row[2] != "ongoing":
        return await message.reply("Сделка ещё не активна или уже завершена.")
    now = datetime.now().isoformat()
    c.execute("UPDATE deals SET status=?, updated_at=? WHERE id=?", ("awaiting_confirmation", now, deal_id))
    conn.commit()
    await message.answer(f"Ты завершил сделку #{deal_id}. Ждём подтверждения получателя.")
    await dp.bot.send_message(row[1], f"🎁 Отправитель завершил сделку #{deal_id}. Если всё в порядке, отправь /confirm {deal_id}")

@dp.message_handler(commands=["confirm"])
async def confirm_finish(message: types.Message):
    args = message.get_args()
    if not args or not args.isdigit():
        return await message.reply("Пример: /confirm 3")
    deal_id = int(args)
    c = conn.cursor()
    c.execute("SELECT buyer, status FROM deals WHERE id=?", (deal_id,))
    row = c.fetchone()
    if not row or row[0] != message.from_user.id:
        return await message.reply("Ты не участник этой сделки.")
    if row[1] != "awaiting_confirmation":
        return await message.reply("Сделка ещё не завершена отправителем.")
    now = datetime.now().isoformat()
    c.execute("UPDATE deals SET status=?, updated_at=? WHERE id=?", ("finished", now, deal_id))
    conn.commit()
    await message.answer(f"Сделка #{deal_id} успешно завершена! 🎉")