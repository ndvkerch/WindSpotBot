import logging
from aiogram import Bot, Dispatcher
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Точка входа для бота."""
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    logger.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
