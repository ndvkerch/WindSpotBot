import aiosqlite
from models.user import User
from typing import Optional

class UserRepository:
    """Репозиторий для работы с пользователями."""
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(self, user_id: int, name: str, username: Optional[str] = None) -> int:
        """Создание пользователя."""
        # TODO: Реализовать SQL-запрос
        return 0

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID."""
        # TODO: Реализовать SQL-запрос
        return None