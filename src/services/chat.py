from aiogram import Bot
from typing import List
from services.topic import TopicService
from config import settings


class ChatService:
    """Сервис для управления чатами спотов."""

    def __init__(self, bot: Bot, topic_service: TopicService):
        self.bot = bot
        self.topic_service = topic_service

    async def get_spot_messages(self, spot_name: str, limit: int) -> List[dict]:
        """Получение сообщений из темы спота."""
        thread_id = await self.topic_service.get_topic_id(spot_name)
        if thread_id:
            # TODO: Реализовать получение сообщений из темы
            return []
        return []
