import aiosqlite
from typing import List, Optional
from src.models.checkin import Checkin
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CheckinRepository:
    """Репозиторий для работы с чек-инами."""

    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(self, checkin: Checkin) -> int:
        """Создание чек-ина."""
        async with self.db.execute(
            "INSERT INTO checkins (user_id, spot_id, type, duration, created_at, active_until, planned_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                checkin.user_id,
                checkin.spot_id,
                checkin.type,
                checkin.duration,
                checkin.created_at.isoformat() if checkin.created_at else None,
                checkin.active_until.isoformat() if checkin.active_until else None,
                checkin.planned_at.isoformat() if checkin.planned_at else None,
            ),
        ) as cursor:
            await self.db.commit()
            checkin_id = cursor.lastrowid
            logger.info(
                f"Чек-ин #{checkin_id} создан для пользователя {checkin.user_id}"
            )
            return checkin_id

    async def get_by_user(self, user_id: int) -> List[Checkin]:
        """Получение чек-инов пользователя."""
        async with self.db.execute(
            "SELECT id, user_id, spot_id, type, duration, created_at, active_until, planned_at "
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
                    created_at=datetime.fromisoformat(row[5]) if row[5] else None,
                    active_until=datetime.fromisoformat(row[6]) if row[6] else None,
                    planned_at=datetime.fromisoformat(row[7]) if row[7] else None,
                )
                for row in rows
            ]

    async def get_by_spot(self, spot_id: int) -> List[Checkin]:
        """Получение чек-инов для спота."""
        try:
            async with self.db.execute(
                "SELECT id, user_id, spot_id, type, duration, created_at, active_until, planned_at "
                "FROM checkins WHERE spot_id = ?",
                (spot_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                checkins = [
                    Checkin(
                        id=row[0],
                        user_id=row[1],
                        spot_id=row[2],
                        type=row[3],
                        duration=row[4],
                        created_at=datetime.fromisoformat(row[5]) if row[5] else None,
                        active_until=datetime.fromisoformat(row[6]) if row[6] else None,
                        planned_at=datetime.fromisoformat(row[7]) if row[7] else None,
                    )
                    for row in rows
                ]
                logger.info(f"Найдено {len(checkins)} чек-инов для спота id {spot_id}")
                return checkins
        except Exception as e:
            logger.error(f"Ошибка при получении чек-инов для спота id {spot_id}: {e}")
            return []

    async def deactivate_checkin(self, checkin_id: int) -> bool:
        """Деактивация чек-ина."""
        try:
            async with self.db.execute(
                "UPDATE checkins SET active_until = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), checkin_id),
            ) as cursor:
                await self.db.commit()
                if cursor.rowcount > 0:
                    logger.info(f"Чек-ин #{checkin_id} деактивирован")
                    return True
                else:
                    logger.warning(f"Чек-ин #{checkin_id} не найден")
                    return False
        except Exception as e:
            logger.error(f"Ошибка при деактивации чек-ина #{checkin_id}: {e}")
            return False
