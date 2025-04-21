import aiohttp
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class WeatherService:
    """Сервис для получения данных о погоде."""

    def __init__(self):
        self.marine_api_url = "https://marine-api.open-meteo.com/v1/marine"
        self.weather_api_url = "https://api.open-meteo.com/v1/forecast"

    async def get_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Получение данных о погоде для координат."""
        try:
            # Запрос к marine-api для water_temperature
            marine_params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": "water_temperature",
            }
            # Запрос к weather-api для wind_speed_10m
            weather_params = {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": "wind_speed_10m",
            }
            async with aiohttp.ClientSession() as session:
                # Запрос к marine-api
                async with session.get(
                    self.marine_api_url, params=marine_params
                ) as marine_response:
                    if marine_response.status != 200:
                        logger.error(
                            f"Ошибка marine API Open-Meteo: {marine_response.status}"
                        )
                        return None
                    marine_data = await marine_response.json()

                # Запрос к weather-api
                async with session.get(
                    self.weather_api_url, params=weather_params
                ) as weather_response:
                    if weather_response.status != 200:
                        logger.error(
                            f"Ошибка weather API Open-Meteo: {weather_response.status}"
                        )
                        return None
                    weather_data = await weather_response.json()

            # Обработка данных
            marine_latest = marine_data.get("daily", {})
            weather_latest = weather_data.get("hourly", {})
            water_temp = marine_latest.get("water_temperature", [None])[-1]
            wind_speed = weather_latest.get("wind_speed_10m", [None])[-1]

            result = {
                "wind_speed": wind_speed,  # м/с
                "water_temperature": water_temp,  # °C
            }
            logger.info(f"Погода получена: {result}")
            return result
        except Exception as e:
            logger.error(f"Ошибка при получении погоды: {e}")
            return None
