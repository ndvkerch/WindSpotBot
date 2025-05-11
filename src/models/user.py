from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class User(BaseModel):
    """Модель пользователя."""

    id: int
    name: str
    username: Optional[str] = None
    timezone: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
