from dotenv import load_dotenv
load_dotenv()
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
