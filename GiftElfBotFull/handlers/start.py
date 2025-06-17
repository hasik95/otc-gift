from aiogram import types
from bot import dp

@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот для обмена подарками 🎁\n\n"
                         "Команды:\n"
                         "/create <описание> — создать сделку\n"
                         "/list — показать все доступные подарки\n"
                         "/mydeals — мои сделки\n"
                         "/cancel <id> — отменить свою сделку\n"
                         "/finish <id> — завершить сделку")
