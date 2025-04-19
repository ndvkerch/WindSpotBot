from aiogram import Bot
from models.user import User
from src.services.topic import TopicService
from src.repositories.subscription import SubscriptionRepository
from src.config import settings
import logging


class NotificationService:
    """Сервис для отправки пуш-уведомлений пользователям."""

    def __init__(
        self,
        bot: Bot,
        topic_service: TopicService,
        subscription_repo: SubscriptionRepository,
    ):
        self.bot = bot
        self.topic_service = topic_service
        self.subscription_repo = subscription_repo

    async def send_checkin_notification(self, user: User, spot_name: str):
        """Отправка уведомления о чек-ине подписчикам."""
        subscribers = await self.subscription_repo.get_subscribers(spot_name, "checkin")
        for user_id in subscribers:
            try:
                await self.bot.send_message(
                    chat_id=user_id,
                    text=f"@{user.username} отметился на споте '{spot_name}'",
                )
            except Exception as e:
                logging.error(
                    f"Ошибка при отправке уведомления пользователю {user_id}: {e}"
                )

    async def send_message_notification(
        self, spot_name: str, message_text: str, sender: User
    ):
        """Отправка уведомления о новом сообщении в чате."""
        subscribers = await self.subscription_repo.get_subscribers(spot_name, "message")
        for user_id in subscribers:
            try:
                await self.bot.send_message(
                    chat_id=user_id,
                    text=f"Новое сообщение в чате '{spot_name}' от @{sender.username}: {message_text[:100]}...",
                )
            except Exception as e:
                logging.error(
                    f"Ошибка при отправке уведомления пользователю {user_id}: {e}"
                )

    async def send_weather_notification(self, spot_name: str, weather_data: dict):
        """Отправка уведомления об изменении ветра."""
        subscribers = await self.subscription_repo.get_subscribers(spot_name, "weather")
        wind_speed = weather_data.get("wind_speed", "N/A")
        for user_id in subscribers:
            try:
                await self.bot.send_message(
                    chat_id=user_id,
                    text=f"Ветер на споте '{spot_name}' изменился: {wind_speed} м/с",
                )
            except Exception as e:
                logging.error(
                    f"Ошибка при отправке уведомления пользователю {user_id}: {e}"
                )

    async def send_spot_checkin_notification(self, user: User, spot_name: str):
        """Отправка уведомления о чек-ине в тему спота."""
        thread_id = await self.topic_service.get_topic_id(spot_name)
        if thread_id:
            try:
                await self.bot.send_message(
                    chat_id=settings.CHAT_ID,
                    message_thread_id=thread_id,
                    text=f"@{user.username} отметился на споте '{spot_name}'",
                )
            except Exception as e:
                logging.error(
                    f"Ошибка при отправке уведомления в тему '{spot_name}': {e}"
                )
