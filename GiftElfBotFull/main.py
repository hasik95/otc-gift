from aiogram import executor
from bot import dp

import handlers.start
import handlers.deals
import handlers.management

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
