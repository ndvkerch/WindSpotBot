import aiohttp

class WeatherService:
    """Сервис для получения погоды."""
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def get_weather(self, lat: float, lon: float) -> dict:
        """Получение погоды для координат."""
        # TODO: Реализовать логику
        return {}