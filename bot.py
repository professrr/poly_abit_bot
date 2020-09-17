from aiogram import executor

from misc import dp
import handlers
import congrats from handlers.a1_say_hello

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=congrats)