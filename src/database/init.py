import aiosqlite
import logging

logger = logging.getLogger(__name__)


async def init_db(db_path: str):
    """Инициализация базы данных."""
    try:
        async with aiosqlite.connect(db_path) as db:
            logger.info("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        raise
