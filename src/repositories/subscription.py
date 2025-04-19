import aiosqlite
from typing import List
from src.models.subscription import Subscription
from datetime import datetime


class SubscriptionRepository:
    """Репозиторий для работы с подписками."""

    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(self, user_id: int, spot_name: str, event_type: str) -> None:
        """Создание подписки."""
        async with self.db.execute(
            "INSERT INTO subscriptions (user_id, spot_name, "
            "event_type, created_at) VALUES (?, ?, ?, ?)",
            (user_id, spot_name, event_type, datetime.utcnow().isoformat()),
        ):
            await self.db.commit()

    async def get_by_user(self, user_id: int) -> List[Subscription]:
        """Получение подписок пользователя."""
        async with self.db.execute(
            "SELECT user_id, spot_name, event_type, created_at "
            "FROM subscriptions WHERE user_id = ?",
            (user_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                Subscription(
                    user_id=row[0],
                    spot_name=row[1],
                    event_type=row[2],
                    created_at=row[3],
                )
                for row in rows
            ]

    async def get_subscribers(self, spot_name: str, event_type: str) -> List[int]:
        """Получение ID пользователей, подписанных на событие."""
        async with self.db.execute(
            "SELECT user_id FROM subscriptions WHERE spot_name = ? AND event_type = ?",
            (spot_name, event_type),
        ) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
