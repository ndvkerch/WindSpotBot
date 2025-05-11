import aiosqlite
import logging
from src.models.user import User
from typing import Optional

logger = logging.getLogger(__name__)


class UserRepository:
    """Репозиторий для работы с таблицей users."""

    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(
        self,
        user_id: int,
        name: str,
        username: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> int:
        """Создание пользователя."""
        try:
            await self.db.execute(
                """
                INSERT INTO users (id, name, username, timezone)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    username = excluded.username,
                    timezone = excluded.timezone
                """,
                (user_id, name, username, timezone),
            )
            await self.db.commit()
            logger.info(f"Пользователь {user_id} создан или обновлен")
            return user_id
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя {user_id}: {e}")
            raise

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID."""
        try:
            cursor = await self.db.execute(
                "SELECT id, name, username, timezone, created_at FROM users WHERE id = ?",
                (user_id,),
            )
            row = await cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    name=row[1],
                    username=row[2],
                    timezone=row[3],
                    created_at=row[4],
                )
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя {user_id}: {e}")
            raise
