from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Настройки бота."""

    BOT_TOKEN: str
    CHAT_ID: str
    ADMINS: List[int]
    NEARBY_SPOTS_LIMIT: int = 5
    PLANNED_VISITS_LIMIT: int = 5
    CHECKIN_CHECK_INTERVAL_MINUTES: int = 5
    WEATHER_CHECK_INTERVAL_MINUTES: int = 15
    MESSAGE_TTL_DAYS: int = 7
    STATS_CACHE_TTL_SECONDS: int = 600
    MAX_SUBSCRIPTIONS_PER_USER: int = 10
    NOTIFICATION_INTERVAL_SECONDS: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
