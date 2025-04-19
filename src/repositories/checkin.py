import aiosqlite
from models.checkin import Checkin
from typing import Optional

class CheckinRepository:
    """Репозиторий для работы с чек-инами."""
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(self, user_id: int, spot_id: int, checkin_type: int, duration: int) -> int:
        """Создание чек-ина."""
        # TODO: Реализовать SQL-запрос
        return 0

    async def get_active_by_user(self, user_id: int) -> Optional[Checkin]:
        """Получение активного чек-ина пользователя."""
        # TODO: Реализовать SQL-запрос
        return None