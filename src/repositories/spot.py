import aiosqlite
from models.spot import Spot
from typing import Optional, List

class SpotRepository:
    """Репозиторий для работы со спотами."""
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(self, name: str, latitude: float, longitude: float, description: Optional[str] = None) -> int:
        """Создание спота."""
        # TODO: Реализовать SQL-запрос
        return 0

    async def get_nearby(self, latitude: float, longitude: float, limit: int) -> List[Spot]:
        """Получение ближайших спотов."""
        # TODO: Реализовать SQL-запрос
        return []