# main.py
import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import payment_handler, start_handler, matrix_handler, numerology_handler, \
    compatibility_handler, user_input_handler, sections_handler, one_question_handler, share_with_friend
from config import BOT_TOKEN
from services.db_service import setup_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"), timeout=150)
dp = Dispatcher(storage=MemoryStorage())


async def main():
    try:
        await setup_db()
        dp.include_router(start_handler.router)
        dp.include_router(matrix_handler.router)
        dp.include_router(user_input_handler.router)
        dp.include_router(numerology_handler.router)
        dp.include_router(compatibility_handler.router)
        dp.include_router(sections_handler.router)
        dp.include_router(one_question_handler.router)
        dp.include_router(payment_handler.router)
        dp.include_router(share_with_friend.router)

        # Start the bot.
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception("An error occurred while running the bot: %s", e)


if __name__ == "__main__":
    asyncio.run(main())
