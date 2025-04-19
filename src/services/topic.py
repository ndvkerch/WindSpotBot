import logging
from aiogram import Bot
from config import settings
from typing import Optional


class TopicService:
    """Сервис для управления темами в @WindSpotChat."""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def create_topic(self, spot_name: str) -> Optional[int]:
        """Создание темы для спота и получение message_thread_id."""
        try:
            topic = await self.bot.create_forum_topic(
                chat_id=settings.CHAT_ID,
                name=spot_name,
                icon_custom_emoji_id=None,  # Можно добавить эмодзи для темы
            )
            thread_id = topic.message_thread_id
            return thread_id
        except Exception as e:
            logging.error(f"Ошибка при создании темы '{spot_name}': {e}")
            return None

    async def get_topic_id(self, spot_name: str) -> Optional[int]:
        """Получение message_thread_id для существующей темы (заглушка)."""
        # TODO: Реализовать запрос к Telegram API для получения списка тем
        return None
