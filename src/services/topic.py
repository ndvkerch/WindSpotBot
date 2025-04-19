import aiosqlite
import logging
from aiogram import Bot
from config import settings
from typing import Optional


class TopicService:
    """Сервис для управления темами в @WindSpotChat."""

    def __init__(self, bot: Bot, db: aiosqlite.Connection):
        self.bot = bot
        self.db = db

    async def create_topic(self, spot_name: str) -> Optional[int]:
        """Создание темы для спота и сохранение message_thread_id в БД."""
        try:
            topic = await self.bot.create_forum_topic(
                chat_id=settings.CHAT_ID, name=spot_name, icon_custom_emoji_id=None
            )
            thread_id = topic.message_thread_id
            if thread_id:
                await self.save_topic_id(spot_name, thread_id)
            return thread_id
        except Exception as e:
            logging.error(f"Ошибка при создании темы '{spot_name}': {e}")
            return None

    async def save_topic_id(self, spot_name: str, thread_id: int):
        """Сохранение message_thread_id в БД."""
        async with self.db.execute(
            "INSERT OR REPLACE INTO spot_topics (spot_name, thread_id) VALUES (?, ?)",
            (spot_name, thread_id),
        ):
            await self.db.commit()

    async def get_topic_id(self, spot_name: str) -> Optional[int]:
        """Получение message_thread_id из БД."""
        async with self.db.execute(
            "SELECT thread_id FROM spot_topics WHERE spot_name = ?", (spot_name,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None
