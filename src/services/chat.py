from aiogram import Bot
from typing import List, Optional
from src.services.topic import TopicService
from src.config import settings


class ChatService:
    """Сервис для управления чатами спотов."""

    def __init__(self, bot: Bot, topic_service: TopicService):
        self.bot = bot
        self.topic_service = topic_service

    async def get_spot_messages(self, spot_name: str, limit: int = 10) -> List[dict]:
        """Получение последних сообщений из темы спота."""
        thread_id = await self.topic_service.get_topic_id(spot_name)
        if not thread_id:
            return []

        # Заглушка: Telegram API не позволяет напрямую получить сообщения из темы
        # Реализация через историю чата (будет доработана в Этапе 2)
        return []

    async def send_message_to_spot(self, spot_name: str, text: str) -> Optional[int]:
        """Отправка сообщения в тему спота."""
        thread_id = await self.topic_service.get_topic_id(spot_name)
        if thread_id:
            try:
                message = await self.bot.send_message(
                    chat_id=settings.CHAT_ID, message_thread_id=thread_id, text=text
                )
                return message.message_id
            except Exception as e:
                logging.error(
                    f"Ошибка при отправке сообщения в тему '{spot_name}': {e}"
                )
        return None

    async def get_chat_activity(self, spot_name: str, hours: int = 24) -> int:
        """Получение количества сообщений в теме за последние N часов (заглушка)."""
        # TODO: Реализовать анализ активности через историю чата
        return 0
