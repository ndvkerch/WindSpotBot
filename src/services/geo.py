from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from src.models.spot import Spot, SpotWithDistance
from src.config.config import settings
import logging
import math
from typing import List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class GeoService:
    """Сервис для работы с геолокацией."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.cache = {}  # Временный кеш: {user_id: (latitude, longitude, timestamp)}

    async def request_location(
        self, message: Message, state: FSMContext, user_id: int
    ) -> Optional[Tuple[float, float]]:
        """Запрос геолокации пользователя."""
        logger.info(
            f"Запрос геолокации для пользователя {user_id}, текущее состояние: {await state.get_state()}"
        )
        try:
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Отправить геолокацию", request_location=True)]
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
            )
            await message.answer("Отправьте вашу геолокацию:", reply_markup=keyboard)
            return None
        except Exception as e:
            logger.error(
                f"Ошибка при запросе геолокации для пользователя {user_id}: {e}"
            )
            return None

    async def process_location(
        self, message: Message, state: FSMContext
    ) -> Optional[Tuple[float, float]]:
        """Обработка полученной геолокации."""
        user_id = message.from_user.id
        logger.info(
            f"Обработка геолокации от пользователя {user_id}, состояние: {await state.get_state()}"
        )
        try:
            if not message.location:
                logger.warning(
                    f"Сообщение не содержит геолокацию для пользователя {user_id}"
                )
                await message.answer("Пожалуйста, отправьте геолокацию.")
                return None
            latitude = message.location.latitude
            longitude = message.location.longitude
            await self.cache_location(user_id, latitude, longitude)
            logger.info(
                f"Геолокация обработана для пользователя {user_id}: ({latitude}, {longitude})"
            )
            return latitude, longitude
        except Exception as e:
            logger.error(
                f"Ошибка при обработке геолокации для пользователя {user_id}: {e}"
            )
            await message.answer(f"Ошибка: {str(e)}")
            return None

    async def get_cached_location(self, user_id: int) -> Optional[Tuple[float, float]]:
        """Получение кэшированных координат."""
        logger.info(f"Проверка кэша геолокации для пользователя {user_id}")
        if user_id not in self.cache:
            logger.info(f"Кэш пуст для пользователя {user_id}")
            return None
        latitude, longitude, timestamp = self.cache[user_id]
        logger.debug(
            f"Найден кэш для пользователя {user_id}: ({latitude}, {longitude}), timestamp: {timestamp}"
        )
        if datetime.utcnow() <= timestamp + timedelta(
            seconds=settings.STATS_CACHE_TTL_SECONDS
        ):
            logger.info(f"Кэш валиден: ({latitude}, {longitude})")
            return latitude, longitude
        logger.info(f"Кэш устарел для пользователя {user_id}, удаление")
        del self.cache[user_id]
        return None

    async def cache_location(self, user_id: int, latitude: float, longitude: float):
        """Кэширование координат."""
        self.cache[user_id] = (latitude, longitude, datetime.utcnow())
        logger.info(
            f"Кэшированы координаты для пользователя {user_id}: ({latitude}, {longitude})"
        )

    def calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Вычисление расстояния между двумя точками (в км)."""
        logger.debug(f"Вычисление расстояния между ({lat1}, {lon1}) и ({lat2}, {lon2})")
        R = 6371  # Радиус Земли в км
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(
            math.radians(lat1)
        ) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        logger.debug(f"Расстояние: {distance} км")
        return distance

    async def get_nearby_spots(
        self, spots: List[Spot], latitude: float, longitude: float
    ) -> List[SpotWithDistance]:
        """Получение ближайших спотов с расстоянием."""
        try:
            logger.info(f"Получение ближайших спотов для ({latitude}, {longitude})")
            if not spots:
                logger.warning("Список спотов пуст")
                return []
            spots_with_distance = [
                SpotWithDistance(
                    spot=spot,
                    distance=self.calculate_distance(
                        latitude, longitude, spot.latitude, spot.longitude
                    ),
                )
                for spot in spots
            ]
            nearby = sorted(spots_with_distance, key=lambda x: x.distance)[
                : settings.NEARBY_SPOTS_LIMIT
            ]
            logger.info(f"Найдено {len(nearby)} ближайших спотов")
            return nearby
        except Exception as e:
            logger.error(f"Ошибка при получении ближайших спотов: {e}")
            return []
