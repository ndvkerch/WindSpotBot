import aiohttp
import logging
from typing import Optional, Dict


class WeatherService:
    """Сервис для получения данных о погоде."""

    def __init__(self):
        self.api_url = "https://marine-api.open-meteo.com/v1/marine"

    async def get_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Получение данных о погоде для координат."""
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": "wind_speed_10m,water_temperature",
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url, params=params) as response:
                    if response.status != 200:
                        logging.error(f"Ошибка API Open-Meteo: {response.status}")
                        return None
                    data = await response.json()
                    # Берём последние доступные данные
                    latest = data.get("hourly", {})
                    wind_speed = latest.get("wind_speed_10m", [None])[-1]
                    water_temp = latest.get("water_temperature", [None])[-1]
                    return {
                        "wind_speed": wind_speed,  # м/с
                        "water_temperature": water_temp,  # °C
                    }
        except Exception as e:
            logging.error(f"Ошибка при получении погоды: {e}")
            return None
