from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.models.spot import Spot
from src.config.config import settings
import logging
import math
from typing import List, Optional, Tuple
from datetime import datetime, timedelta


class GeoStates(StatesGroup):
    """Состояния для запроса геолокации."""

    requesting_location = State()


class GeoService:
    """Сервис для работы с геолокацией."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.cache = {}  # Временный кеш: {user_id: (latitude, longitude, timestamp)}

    async def request_location(
        self, message: types.Message, state: FSMContext
    ) -> Optional[Tuple[float, float]]:
        """Запрос геолокации пользователя."""
        try:
            await message.answer("Отправьте вашу геолокацию:")
            await state.set_state(GeoStates.requesting_location)
            return None
        except Exception as e:
            logging.error(f"Ошибка при запросе геолокации: {e}")
            return None

    async def process_location(
        self, message: types.Message, state: FSMContext
    ) -> Optional[Tuple[float, float]]:
        """Обработка полученной геолокации."""
        try:
            if not message.location:
                await message.answer("Пожалуйста, отправьте геолокацию.")
                return None
            latitude = message.location.latitude
            longitude = message.location.longitude
            await self.cache_location(message.from_user.id, latitude, longitude)
            await state.clear()
            return latitude, longitude
        except Exception as e:
            logging.error(f"Ошибка при обработке геолокации: {e}")
            await message.answer(f"Ошибка: {str(e)}")
            return None

    async def get_cached_location(self, user_id: int) -> Optional[Tuple[float, float]]:
        """Получение кэшированных координат."""
        if user_id in self.cache:
            latitude, longitude, timestamp = self.cache[user_id]
            if datetime.utcnow() < timestamp + timedelta(
                seconds=settings.STATS_CACHE_TTL_SECONDS
            ):
                return latitude, longitude
            else:
                del self.cache[user_id]
        return None

    async def cache_location(self, user_id: int, latitude: float, longitude: float):
        """Кэширование координат."""
        self.cache[user_id] = (latitude, longitude, datetime.utcnow())
        logging.info(
            f"Кэшированы координаты для пользователя {user_id}: ({latitude}, {longitude})"
        )

    def calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Вычисление расстояния между двумя точками (в км)."""
        R = 6371  # Радиус Земли в км
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(
            math.radians(lat1)
        ) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    async def get_nearby_spots(
        self, spots: List[Spot], latitude: float, longitude: float
    ) -> List[Spot]:
        """Получение ближайших спотов."""
        try:
            if not spots:
                return []
            # Добавляем расстояние к спотам
            for spot in spots:
                spot.distance = self.calculate_distance(
                    latitude, longitude, spot.latitude, spot.longitude
                )
            # Сортируем и ограничиваем
            return sorted(spots, key=lambda x: x.distance)[
                : settings.NEARBY_SPOTS_LIMIT
            ]
        except Exception as e:
            logging.error(f"Ошибка при получении ближайших спотов: {e}")
            return []
