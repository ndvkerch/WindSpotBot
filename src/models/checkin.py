from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Checkin(BaseModel):
    """Модель чек-ина."""
    id: int
    user_id: int
    spot_id: int
    type: int  # 1: На месте, 2: Прибуду, 3: Планирование
    duration: int  # в секундах
    created_at: datetime
    active_until: Optional[datetime] = None
    planned_at: Optional[datetime] = None