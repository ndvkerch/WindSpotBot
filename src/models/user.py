from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    """Модель пользователя."""
    id: int
    name: str
    username: Optional[str] = None
    timezone: Optional[str] = None