from aiogram import Bot
from models.user import User
from services.topic import TopicService
from config import settings


class NotificationService:
    """Сервис для отправки уведомлений."""

    def __init__(self, bot: Bot, topic_service: TopicService):
        self.bot = bot
        self.topic_service = topic_service

    async def send_checkin_notification(self, user: User, spot_name: str):
        """Отправка уведомления о чек-ине в тему спота."""
        thread_id = await self.topic_service.get_topic_id(spot_name)
        if thread_id:
            await self.bot.send_message(
                chat_id=settings.CHAT_ID,
                message_thread_id=thread_id,
                text=f"@{user.username} отметился на споте '{spot_name}'",
            )
