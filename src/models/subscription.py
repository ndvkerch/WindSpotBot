from pydantic import BaseModel
from typing import Optional


class Subscription(BaseModel):
    """Модель подписки пользователя на события."""

    user_id: int
    spot_name: str
    event_type: str  # checkin, message, weather
    created_at: Optional[str] = None
