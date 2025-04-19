from repositories.spot import SpotRepository
from models.spot import Spot
from typing import List

class SpotService:
    """Сервис для управления спотами."""
    def __init__(self, spot_repo: SpotRepository):
        self.spot_repo = spot_repo

    async def get_nearby_spots(self, lat: float, lon: float, limit: int) -> List[Spot]:
        """Получение ближайших спотов."""
        # TODO: Реализовать логику
        return await self.spot_repo.get_nearby(lat, lon, limit)

    async def invalidate_spot_cache(self, lat: Optional[float], lon: Optional[float]):
        """Сброс кэша спотов."""
        # TODO: Реализовать логику
        pass