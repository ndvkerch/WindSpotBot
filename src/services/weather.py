import aiohttp
import logging
import math
from datetime import datetime
import asyncio
from aiocache import Cache, cached
from typing import Optional, Dict

logger = logging.getLogger(__name__)
cache = Cache(Cache.MEMORY)


class WeatherService:
    """Сервис для получения данных о погоде с Open-Meteo."""

    @cached(ttl=1800, key_builder=lambda *args, **kwargs: f"wind_{args[1]}_{args[2]}")
    async def get_wind_data(
        self, lat: float, lon: float, force_refresh: bool = False
    ) -> Optional[Dict]:
        """Получает данные о ветре с Open-Meteo Forecast API."""
        cache_key = f"wind_{lat}_{lon}"
        if force_refresh:
            await cache.delete(cache_key)
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=windspeed_10m,winddirection_10m,windgusts_10m&"
            f"windspeed_unit=ms&timezone=auto"
        )
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5)
            ) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(
                            f"Ошибка Open-Meteo Wind API: status={response.status}"
                        )
                        return None
                    data = await response.json()
                    if "current" not in data:
                        logger.error("Отсутствует ключ 'current' в ответе Open-Meteo")
                        return None
                    current = data["current"]
                    wind_speed = current.get("windspeed_10m")
                    wind_direction = current.get("winddirection_10m")
                    wind_gusts = current.get("windgusts_10m")
                    if wind_speed is None or wind_direction is None:
                        logger.error("Данные о ветре отсутствуют в current")
                        return None
                    logger.info(f"Данные о ветре получены для lat={lat}, lon={lon}")
                    return {
                        "wind_speed": wind_speed,
                        "wind_direction": wind_direction,
                        "wind_gusts": wind_gusts,
                    }
        except Exception as e:
            logger.error(f"Ошибка при запросе ветра: {e}")
            return None

    @cached(ttl=3600, key_builder=lambda *args, **kwargs: f"water_{args[1]}_{args[2]}")
    async def get_water_temp(
        self, lat: float, lon: float, force_refresh: bool = False
    ) -> Optional[float]:
        """Получает температуру воды с Open-Meteo Marine API."""
        cache_key = f"water_{lat}_{lon}"
        if force_refresh:
            await cache.delete(cache_key)
        url = (
            f"https://marine-api.open-meteo.com/v1/marine?"
            f"latitude={lat}&longitude={lon}&hourly=sea_surface_temperature"
        )
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5)
            ) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(
                            f"Ошибка Open-Meteo Marine API: status={response.status}"
                        )
                        return None
                    data = await response.json()
                    hourly = data.get("hourly", {})
                    times = hourly.get("time", [])
                    temps = hourly.get("sea_surface_temperature", [])
                    if not times or not temps:
                        logger.warning(
                            f"Температура воды недоступна для lat={lat}, lon={lon}"
                        )
                        return None
                    # Найти ближайшее время
                    current_time = datetime.utcnow().timestamp()
                    index = min(
                        range(len(times)),
                        key=lambda i: abs(
                            datetime.fromisoformat(
                                times[i].replace("Z", "+00:00")
                            ).timestamp()
                            - current_time
                        ),
                    )
                    water_temp = temps[index]
                    logger.info(
                        f"Температура воды получена для lat={lat}, lon={lon}: {water_temp}°C"
                    )
                    return water_temp
        except Exception as e:
            logger.error(f"Ошибка при запросе температуры воды: {e}")
            return None

    async def get_weather(
        self, latitude: float, longitude: float, force_refresh: bool = False
    ) -> Optional[Dict]:
        """
        Получает текущие данные о ветре, порывах ветра, направлении и температуре воды с Open-Meteo.

        Args:
            latitude (float): Широта точки.
            longitude (float): Долгота точки.
            force_refresh (bool): Если True, отключает кэширование.

        Returns:
            Optional[Dict]: Словарь с данными о ветре (скорость, направление, порывы) и температуре воды (°C).
                           Если данные недоступны, возвращается None.
        """
        wind_task, water_task = await asyncio.gather(
            self.get_wind_data(latitude, longitude, force_refresh),
            self.get_water_temp(latitude, longitude, force_refresh),
            return_exceptions=True,
        )

        result = {
            "wind_speed": None,
            "wind_direction": None,
            "wind_gusts": None,
            "water_temperature": None,
        }
        if isinstance(wind_task, dict):
            result.update(wind_task)
        elif wind_task is not None:
            logger.error(f"Ошибка в wind_task: {wind_task}")
        if isinstance(water_task, float):
            result["water_temperature"] = water_task
        elif water_task is not None:
            logger.error(f"Ошибка в water_task: {water_task}")

        if all(value is None for value in result.values()):
            logger.warning(
                f"Все данные о погоде недоступны для lat={latitude}, lon={longitude}"
            )
            return None
        return result

    @staticmethod
    def wind_direction_to_text(degrees: Optional[float]) -> str:
        """Преобразование градусов направления ветра в текстовое описание."""
        if degrees is None:
            return "N/A"
        directions = [
            "С",
            "ССВ",
            "СВ",
            "ВСВ",
            "В",
            "ВЮВ",
            "ЮВ",
            "ЮЮВ",
            "Ю",
            "ЮЮЗ",
            "ЮЗ",
            "ЗЮЗ",
            "З",
            "ЗСЗ",
            "СЗ",
            "ССЗ",
        ]
        index = round(degrees / 22.5) % 16
        return directions[index]
