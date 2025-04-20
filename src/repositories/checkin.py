import aiosqlite
from typing import List, Optional
from src.models.checkin import Checkin
from datetime import datetime


class CheckinRepository:
    """Репозиторий для работы с чек-инами."""

    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(self, checkin: Checkin) -> int:
        """Создание чек-ина."""
        async with self.db.execute(
            "INSERT INTO checkins (user_id, spot_id, type, duration, created_at, active_until, planned_at, description) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                checkin.user_id,
                checkin.spot_id,
                checkin.type,
                checkin.duration,
                checkin.created_at,
                checkin.active_until,
                checkin.planned_at,
                checkin.description,
            ),
        ) as cursor:
            await self.db.commit()
            return cursor.lastrowid

    async def get_by_user(self, user_id: int) -> List[Checkin]:
        """Получение чек-инов пользователя."""
        async with self.db.execute(
            "SELECT id, user_id, spot_id, type, duration, created_at, active_until, planned_at, description "
            "FROM checkins WHERE user_id = ?",
            (user_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                Checkin(
                    id=row[0],
                    user_id=row[1],
                    spot_id=row[2],
                    type=row[3],
                    duration=row[4],
                    created_at=row[5],
                    active_until=row[6],
                    planned_at=row[7],
                    description=row[8],
                )
                for row in rows
            ]
