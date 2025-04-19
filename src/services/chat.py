from aiogram import Bot
from typing import List, Optional
from src.services.topic import TopicService
from src.config.config import settings
import logging


class ChatService:
    """Сервис для управления чатами спотов."""

    def __init__(self, bot: Bot, topic_service: TopicService):
        self.bot = bot
        self.topic_service = topic_service

    async def send_message_to_spot(
        self, spot_name: str, text: str, user_id: int
    ) -> Optional[int]:
        """Отправка сообщения в тему спота, создание темы при необходимости."""
        thread_id = await self.topic_service.get_topic_id(spot_name)
        if not thread_id:
            # Создание темы, если она отсутствует
            thread_id = await self.topic_service.create_topic(spot_name)
            if not thread_id:
                logging.error(f"Не удалось создать тему для спота '{spot_name}'")
                return None

        try:
            message = await self.bot.send_message(
                chat_id=settings.CHAT_ID, message_thread_id=thread_id, text=text
            )
            # Уведомление подписчиков о новом сообщении
            from src.models.user import User

            user = User(id=user_id, username="unknown", name="Unknown")
            await NotificationService(
                self.bot, self.topic_service, None
            ).send_message_notification(spot_name, text, user)
            return message.message_id
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения в тему '{spot_name}': {e}")
            return None

    async def get_spot_messages(self, spot_name: str, limit: int = 10) -> List[dict]:
        """Получение последних сообщений из темы спота (заглушка)."""
        thread_id = await self.topic_service.get_topic_id(spot_name)
        if not thread_id:
            return []

        # TODO: Реализовать получение сообщений через Telegram API (будет в Этапе 2)
        return []

    async def get_chat_activity(self, spot_name: str, hours: int = 24) -> int:
        """Получение количества сообщений в теме за последние N часов (заглушка)."""
        # TODO: Реализовать анализ активности через историю чата
        return 0
