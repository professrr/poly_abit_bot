from aiogram import executor

from misc import dp
import handlers
from handlers.a1_say_hello import congrats

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
