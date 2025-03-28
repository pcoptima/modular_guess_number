import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from states import GameStates
from dotenv import load_dotenv
import os
from db import init_db
from aiogram import Router, F
from handlers.user_handlers import (send_welcome, process_help, process_rules, process_settings,
                                    process_set_range, set_range, process_set_time,
                                    process_set_attempts, set_attempts, set_time,
                                    process_my_settings)
from handlers.play_handlers import process_play  # Обновляем импорт

load_dotenv()

API_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

dp.include_router(router)

router.message.register(send_welcome, Command("start"))
router.message.register(process_help, Command("help"))
router.callback_query.register(process_rules, F.data == "rules")
router.callback_query.register(process_settings, F.data == "settings")
router.callback_query.register(process_my_settings, F.data == "my_settings")
router.callback_query.register(process_set_range, F.data == "set_range")
router.callback_query.register(process_set_time, F.data == "set_time")
router.callback_query.register(process_set_attempts, F.data == "set_attempts")
router.message.register(set_range, GameStates.set_range)
router.message.register(set_time, GameStates.set_time)
router.message.register(set_attempts, GameStates.set_attempts)
router.callback_query.register(process_play, F.data == "play")


async def main():
    await init_db()  # Вызываем инициализацию базы данных
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
