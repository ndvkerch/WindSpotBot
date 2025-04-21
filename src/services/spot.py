from typing import List, Optional
from src.models.spot import Spot
from src.repositories.spot import SpotRepository
import logging


class SpotService:
    """Сервис для работы со спотами."""

    def __init__(self, spot_repo: SpotRepository):
        self.spot_repo = spot_repo

    async def add_spot(
        self,
        name: str,
        latitude: float,
        longitude: float,
        created_by: int,
        description: Optional[str] = None,
    ) -> Optional[int]:
        """Добавление спота, возвращает ID."""
        try:
            spot = Spot(
                id=0,
                name=name,
                latitude=latitude,
                longitude=longitude,
                description=description,
                created_by=created_by,
            )
            spot_id = await self.spot_repo.create(spot)
            logging.info(
                f"Спот '{name}' добавлен пользователем {created_by}, id: {spot_id}"
            )
            return spot_id
        except Exception as e:
            logging.error(f"Ошибка при добавлении спота '{name}': {e}")
            return None

    async def get_spot(self, name: str) -> Optional[Spot]:
        """Получение спота по имени."""
        return await self.spot_repo.get_by_name(name)

    async def get_spot_by_id(self, spot_id: int) -> Optional[Spot]:
        """Получение спота по ID."""
        return await self.spot_repo.get_by_id(spot_id)

    async def get_all_spots(self) -> List[Spot]:
        """Получение всех спотов."""
        return await self.spot_repo.get_all()
