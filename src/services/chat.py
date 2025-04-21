from aiogram import Bot
from typing import List, Optional
from src.services.topic import TopicService
from src.services.notification import NotificationService
from src.config.config import settings
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """Сервис для управления чатами спотов."""

    def __init__(
        self,
        bot: Bot,
        topic_service: TopicService,
        notification_service: NotificationService,
    ):
        self.bot = bot
        self.topic_service = topic_service
        self.notification_service = notification_service

    async def send_message_to_spot(
        self, spot_name: str, text: str, user_id: int
    ) -> Optional[int]:
        """Отправка сообщения в тему спота, создание темы при необходимости."""
        logger.info(f"Попытка отправить сообщение в тему '{spot_name}'")
        thread_id = await self.topic_service.get_topic_id(spot_name)
        if not thread_id:
            logger.info(f"Тема '{spot_name}' не найдена, создаём новую")
            thread_id = await self.topic_service.create_topic(spot_name)
            if not thread_id:
                logger.error(f"Не удалось создать тему для спота '{spot_name}'")
                return None
            logger.info(f"Тема '{spot_name}' создана, thread_id: {thread_id}")

        try:
            message = await self.bot.send_message(
                chat_id=settings.CHAT_ID, message_thread_id=thread_id, text=text
            )
            # Уведомление подписчиков о новом сообщении
            from src.models.user import User

            user = User(id=user_id, username="unknown", name="Unknown")
            await self.notification_service.send_message_notification(
                spot_name, text, user
            )
            logger.info(
                f"Сообщение отправлено в тему '{spot_name}', message_id: {message.message_id}"
            )
            return message.message_id
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в тему '{spot_name}': {e}")
            return None

    async def get_chat_link(self, spot_name: str) -> Optional[str]:
        """Получение ссылки на чат спота, создание темы при необходимости."""
        try:
            thread_id = await self.topic_service.get_topic_id(spot_name)
            if not thread_id:
                logger.info(f"Тема '{spot_name}' не найдена, создаём новую")
                thread_id = await self.topic_service.create_topic(spot_name)
                if not thread_id:
                    logger.error(f"Не удалось создать тему для спота '{spot_name}'")
                    return None
                logger.info(f"Тема '{spot_name}' создана, thread_id: {thread_id}")
            chat = await self.bot.get_chat(settings.CHAT_ID)
            return f"https://t.me/{chat.username}/{thread_id}"
        except Exception as e:
            logger.error(f"Ошибка при получении ссылки на чат '{spot_name}': {e}")
            return None

    async def get_spot_messages(self, spot_name: str, limit: int = 10) -> List[dict]:
        """Получение последних сообщений из темы спота (заглушка)."""
        thread_id = await self.topic_service.get_topic_id(spot_name)
        if not thread_id:
            logger.warning(f"Тема '{spot_name}' не найдена")
            return []

        # TODO: Реализовать получение сообщений через Telegram API (Этап 2)
        return []

    async def get_chat_activity(self, spot_name: str, hours: int = 24) -> int:
        """Получение количества сообщений в теме за последние N часов (заглушка)."""
        # TODO: Реализовать анализ активности (Этап 2)
        return 0
