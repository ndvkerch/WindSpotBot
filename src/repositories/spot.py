import aiosqlite
from typing import List, Optional
from src.models.spot import Spot


class SpotRepository:
    """Репозиторий для работы со спотами."""

    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(self, spot: Spot) -> int:
        """Создание спота, возвращает ID."""
        async with self.db.execute(
            "INSERT INTO spots (name, latitude, longitude, description, created_by) VALUES (?, ?, ?, ?, ?)",
            (
                spot.name,
                spot.latitude,
                spot.longitude,
                spot.description,
                spot.created_by,
            ),
        ) as cursor:
            await self.db.commit()
            return cursor.lastrowid

    async def get_by_name(self, name: str) -> Optional[Spot]:
        """Получение спота по имени."""
        async with self.db.execute(
            "SELECT id, name, latitude, longitude, description, created_by FROM spots WHERE name = ?",
            (name,),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return Spot(
                    id=row[0],
                    name=row[1],
                    latitude=row[2],
                    longitude=row[3],
                    description=row[4],
                    created_by=row[5],
                )
            return None

    async def get_by_id(self, spot_id: int) -> Optional[Spot]:
        """Получение спота по ID."""
        async with self.db.execute(
            "SELECT id, name, latitude, longitude, description, created_by FROM spots WHERE id = ?",
            (spot_id,),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return Spot(
                    id=row[0],
                    name=row[1],
                    latitude=row[2],
                    longitude=row[3],
                    description=row[4],
                    created_by=row[5],
                )
            return None

    async def get_all(self) -> List[Spot]:
        """Получение всех спотов."""
        async with self.db.execute(
            "SELECT id, name, latitude, longitude, description, created_by FROM spots"
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                Spot(
                    id=row[0],
                    name=row[1],
                    latitude=row[2],
                    longitude=row[3],
                    description=row[4],
                    created_by=row[5],
                )
                for row in rows
            ]
