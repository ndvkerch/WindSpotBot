from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import Optional


class User(BaseModel):
    """Модель пользователя."""

    id: int
    name: str
    username: Optional[str] = None
    timezone: Optional[str] = None

    model_config = ConfigDict(extra="allow", from_attributes=True)
