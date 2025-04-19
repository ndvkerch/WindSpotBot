from aiogram import Bot
from typing import List


class ChatService:
    """Сервис для управления чатами спотов."""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def filter_messages(self, spot_name: str, limit: int) -> List[dict]:
        """Фильтрация сообщений по хэштегу спота."""
        # TODO: Реализовать логику
        return []
