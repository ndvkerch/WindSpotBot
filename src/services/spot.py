from typing import List, Optional, Tuple
from src.models.spot import Spot
from src.repositories.spot import SpotRepository
from src.services.geo import GeoService
from src.config.config import settings
import logging


class SpotService:
    """Сервис для работы со спотами."""

    def __init__(self, spot_repo: SpotRepository, geo_service: GeoService):
        self.spot_repo = spot_repo
        self.geo_service = geo_service

    async def add_spot(
        self,
        name: str,
        latitude: float,
        longitude: float,
        created_by: int,
        description: Optional[str] = None,
    ) -> Tuple[Optional[int], Optional[str]]:
        """Добавление спота, возвращает ID и сообщение об ошибке (если есть)."""
        try:
            # Проверка на близость к существующим спотам
            spots = await self.spot_repo.get_all()
            for spot in spots:
                distance = (
                    self.geo_service.calculate_distance(
                        latitude, longitude, spot.latitude, spot.longitude
                    )
                    * 1000
                )  # в метрах
                if distance < settings.MIN_SPOT_DISTANCE_M:
                    return (
                        None,
                        f"Спот слишком близко к '{spot.name}' ({distance:.1f} м). Используйте существующий спот.",
                    )

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
            return spot_id, None
        except Exception as e:
            logging.error(f"Ошибка при добавлении спота '{name}': {e}")
            return None, str(e)

    async def get_spot(self, name: str) -> Optional[Spot]:
        """Получение спота по имени."""
        return await self.spot_repo.get_by_name(name)

    async def get_spot_by_id(self, spot_id: int) -> Optional[Spot]:
        """Получение спота по ID."""
        return await self.spot_repo.get_by_id(spot_id)

    async def get_all_spots(self) -> List[Spot]:
        """Получение всех спотов."""
        return await self.spot_repo.get_all()
