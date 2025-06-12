import aiosqlite
from typing import List, Optional
from src.models.checkin import Checkin
import logging
from datetime import datetime, date, timedelta

logger = logging.getLogger(__name__)

class CheckinRepository:
    """Репозиторий для работы с чек-инами."""

    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(self, checkin: Checkin) -> int:
        """Создание чек-ина."""
        try:
            async with self.db.execute(
                "INSERT INTO checkins (user_id, spot_id, type, duration, created_at, active_until, planned_at, active, planned_date) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    checkin.user_id,
                    checkin.spot_id,
                    checkin.type,
                    checkin.duration,
                    checkin.created_at.isoformat(),
                    checkin.active_until.isoformat() if checkin.active_until else None,
                    checkin.planned_at.isoformat() if checkin.planned_at else None,
                    int(checkin.active),
                    checkin.planned_date.isoformat() if checkin.planned_date else None,
                ),
            ) as cursor:
                await self.db.commit()
                checkin_id = cursor.lastrowid
                logger.info(
                    f"Чек-ин #{checkin_id} создан для пользователя {checkin.user_id}"
                )
                return checkin_id
        except Exception as e:
            logger.error(f"Ошибка при создании чек-ина: {e}")
            raise

    async def get_by_user(self, user_id: int) -> List[Checkin]:
        """Получение активных чек-инов пользователя."""
        try:
            async with self.db.execute(
                "SELECT id, user_id, spot_id, type, duration, created_at, active_until, planned_at, active, planned_date "
                "FROM checkins WHERE user_id = ? AND active = 1",
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [Checkin.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении чек-инов пользователя {user_id}: {e}")
            return []

    async def get_by_spot(self, spot_id: int) -> List[Checkin]:
        """Получение всех чек-инов для спота."""
        try:
            async with self.db.execute(
                "SELECT id, user_id, spot_id, type, duration, created_at, active_until, planned_at, active, planned_date "
                "FROM checkins WHERE spot_id = ?",
                (spot_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [Checkin.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении чек-инов для спота {spot_id}: {e}")
            return []

    async def get_by_id(self, checkin_id: int) -> Optional[Checkin]:
        """Получение чек-ина по ID."""
        try:
            async with self.db.execute(
                "SELECT id, user_id, spot_id, type, duration, created_at, active_until, planned_at, active, planned_date "
                "FROM checkins WHERE id = ?",
                (checkin_id,),
            ) as cursor:
                row = await cursor.fetchone()
                return Checkin.from_row(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении чек-ина #{checkin_id}: {e}")
            return None

    async def get_active_checkins(
        self, type_filter: int = None, exclude_date: date = None, max_date: date = None
    ) -> List[Checkin]:
        """Получение всех активных чек-инов с фильтрацией по типу и датам."""
        try:
            now = datetime.utcnow().isoformat()
            query = (
                "SELECT id, user_id, spot_id, type, duration, created_at, active_until, planned_at, active, planned_date "
                "FROM checkins WHERE active = 1 AND (active_until IS NULL OR active_until > ?)"
            )
            params = [now]

            if type_filter is not None:
                query += " AND type = ?"
                params.append(type_filter)

            if exclude_date is not None:
                query += " AND planned_date != ?"
                params.append(exclude_date.isoformat())

            if max_date is not None:
                query += " AND planned_date <= ?"
                params.append(max_date.isoformat())

            async with self.db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [Checkin.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении активных чек-инов: {e}")
            return []

    async def get_expired_checkins(self) -> List[Checkin]:
        """Получение истекших активных чек-инов."""
        try:
            now = datetime.utcnow().isoformat()
            async with self.db.execute(
                "SELECT id, user_id, spot_id, type, duration, created_at, active_until, planned_at, active, planned_date "
                "FROM checkins WHERE active = 1 AND active_until IS NOT NULL AND active_until < ?",
                (now,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [Checkin.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении истекших чек-инов: {e}")
            return []

    async def get_todays_planned_checkins(self, current_date: date) -> List[Checkin]:
        """Получение чек-инов типа 3 для текущей даты."""
        try:
            async with self.db.execute(
                "SELECT id, user_id, spot_id, type, duration, created_at, active_until, planned_at, active, planned_date "
                "FROM checkins WHERE type = 3 AND active = 1 AND planned_date = ?",
                (current_date.isoformat(),),
            ) as cursor:
                rows = await cursor.fetchall()
                checkins = [Checkin.from_row(row) for row in rows]
                logger.debug(f"Найдено {len(checkins)} чек-инов типа 3 на {current_date} в базе")
                return checkins
        except Exception as e:
            logger.error(f"Ошибка при получении чек-инов типа 3 на {current_date}: {e}")
            return []

    async def delete_expired_type_3_checkins(self) -> int:
        """Удаление истекших чек-инов типа 3."""
        try:
            now = datetime.utcnow().isoformat()
            async with self.db.execute(
                "DELETE FROM checkins WHERE type = 3 AND active_until IS NOT NULL AND active_until < ?",
                (now,),
            ) as cursor:
                await self.db.commit()
                deleted_count = cursor.rowcount
                if deleted_count > 0:
                    logger.info(f"Удалено {deleted_count} истекших чек-инов типа 3")
                else:
                    logger.debug(f"Не найдено истекших чек-инов типа 3 на {now}")
                return deleted_count
        except Exception as e:
            logger.error(f"Ошибка при удалении истекших чек-инов типа 3: {e}")
            return 0

    async def deactivate_checkin(
        self, checkin_id: int, update_duration: bool = False
    ) -> bool:
        """Деактивация чек-ина с возможностью обновления duration."""
        try:
            checkin = await self.get_by_id(checkin_id)
            if not checkin or not checkin.active:
                logger.warning(f"Чек-ин #{checkin_id} не найден или уже неактивен")
                return False

            if update_duration:
                now = datetime.utcnow()
                duration = int((now - checkin.created_at).total_seconds())
                async with self.db.execute(
                    "UPDATE checkins SET active_until = ?, duration = ?, active = 0 WHERE id = ?",
                    (now.isoformat(), duration, checkin_id),
                ) as cursor:
                    await self.db.commit()
            else:
                async with self.db.execute(
                    "UPDATE checkins SET active = 0 WHERE id = ?",
                    (checkin_id,),
                ) as cursor:
                    await self.db.commit()

            if cursor.rowcount > 0:
                logger.info(f"Чек-ин #{checkin_id} деактивирован")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка при деактивации чек-ина #{checkin_id}: {e}")
            return False

    async def update_active_until(
        self, checkin_id: int, active_until: datetime, duration: int
    ) -> bool:
        """Обновление active_until и duration для чек-ина."""
        try:
            async with self.db.execute(
                "UPDATE checkins SET active_until = ?, duration = ? WHERE id = ?",
                (active_until.isoformat(), duration, checkin_id),
            ) as cursor:
                await self.db.commit()
                if cursor.rowcount > 0:
                    logger.info(
                        f"Чек-ин #{checkin_id} обновлен: active_until={active_until}, duration={duration}"
                    )
                    return True
                return False
        except Exception as e:
            logger.error(f"Ошибка при обновлении чек-ина #{checkin_id}: {e}")
            return False

    async def get_planned_by_user(self, user_id: int) -> List[Checkin]:
        """Получение активных чек-инов типа 3 для пользователя."""
        try:
            async with self.db.execute(
                "SELECT id, user_id, spot_id, type, duration, created_at, active_until, planned_at, active, planned_date "
                "FROM checkins WHERE user_id = ? AND type = 3 AND active = 1",
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [Checkin.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении чек-инов типа 3 для пользователя {user_id}: {e}")
            return []
