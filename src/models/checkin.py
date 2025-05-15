from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Checkin(BaseModel):
    """Модель чек-ина."""

    id: int
    user_id: int
    spot_id: int
    type: int  # 1: На месте, 2: Прибуду, 3: Планирование
    duration: Optional[int] = None  # Опциональное для типа 3
    created_at: datetime
    active_until: Optional[datetime] = None
    planned_at: Optional[datetime] = None
    active: bool = True  # Новое поле для отслеживания активности
    planned_date: Optional[date] = None  # Новое поле для типа 3

    @classmethod
    def from_row(cls, row):
        """Преобразование строки из базы данных в объект Checkin."""
        try:
            logger.debug(f"Обработка строки: {row}")
            # Проверка на количество полей
            if len(row) != 10:  # Обновлено с 11 на 10 из-за удаления planned_time
                raise ValueError(f"Ожидалось 10 полей, получено {len(row)}: {row}")

            # Преобразование полей
            id_val = row[0]
            user_id_val = row[1]
            spot_id_val = row[2]
            type_val = row[3]
            duration_val = row[4]

            # Функция для парсинга даты с поддержкой разных форматов
            def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
                if not dt_str:
                    return None
                dt_str = dt_str.split('.')[0]
                if 'T' in dt_str:
                    return datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S')
                return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')

            # Функция для парсинга даты (без времени)
            def parse_date(date_str: Optional[str]) -> Optional[date]:
                if not date_str:
                    return None
                return datetime.strptime(date_str, '%Y-%m-%d').date()

            created_at_val = parse_datetime(row[5])
            active_until_val = parse_datetime(row[6])
            planned_at_val = parse_datetime(row[7])
            active_val = bool(row[8])
            planned_date_val = parse_date(row[9])

            if created_at_val is None:
                raise ValueError("Поле created_at не может быть NULL")

            return cls(
                id=id_val,
                user_id=user_id_val,
                spot_id=spot_id_val,
                type=type_val,
                duration=duration_val,
                created_at=created_at_val,
                active_until=active_until_val,
                planned_at=planned_at_val,
                active=active_val,
                planned_date=planned_date_val,
            )
        except Exception as e:
            logger.error(f"Ошибка в Checkin.from_row: {e}, строка: {row}")
            raise
