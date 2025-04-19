from aiogram import Bot
from models.user import User


class NotificationService:
    """Сервис для отправки уведомлений."""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_checkin_notification(self, user: User, spot_name: str):
        """Отправка уведомления о чек-ине."""
        # TODO: Реализовать логику
        pass
