from pydantic import BaseModel
from typing import Optional

class Spot(BaseModel):
    """Модель спота."""
    id: int
    name: str
    latitude: float
    longitude: float
    description: Optional[str] = None