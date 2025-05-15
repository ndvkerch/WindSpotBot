from aiogram import Bot
from src.models.checkin import Checkin
from src.repositories.checkin import CheckinRepository
from src.repositories.user import UserRepository
from src.services.notification import NotificationService
from src.services.spot import SpotService
from src.services.weather import WeatherService
from src.models.user import User
from src.keyboards.main import MainKeyboards
from datetime import datetime, timedelta
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

class CheckinService:
    """Сервис для управления чек-инами."""

    def __init__(
        self,
        bot: Bot,
        checkin_repo: CheckinRepository,
        notification_service: NotificationService,
        spot_service: SpotService,
        user_repo: UserRepository,
        weather_service: WeatherService,
    ):
        self.bot = bot
        self.checkin_repo = checkin_repo
        self.notification_service = notification_service
        self.spot_service = spot_service
        self.user_repo = user_repo
        self.weather_service = weather_service

    async def create_checkin(
        self, user: User, spot_id: int, checkin_type: int, duration: int = 3600
    ) -> bool:
        """Создание чек-ина с автоматическим расчек-ином, если есть активный."""
        try:
            # Проверка существования спота
            spot = await self.spot_service.get_spot_by_id(spot_id)
            if not spot:
                logger.error(f"Спот с id {spot_id} не найден")
                await self.bot.send_message(
                    user.id, f"😕 Спот с ID {spot_id} не найден, бро!"
                )
                return False

            # Проверка существования пользователя
            user_data = await self.user_repo.get_by_id(user.id)
            if not user_data:
                logger.error(f"Пользователь с id {user.id} не найден")
                await self.bot.send_message(user.id, f"😕 Пользователь не найден, бро!")
                return False

            # Проверка активных чек-инов
            checkins = await self.checkin_repo.get_by_user(user.id)
            now = datetime.utcnow()
            previous_checkin = None
            previous_spot_name = None
            logger.info(f"Найдено {len(checkins)} активных чек-инов для пользователя {user.id}")
            for checkin in checkins:
                if (
                    checkin.type in [1, 2]
                    and checkin.active_until
                    and now < checkin.active_until
                    and checkin.active
                ):
                    previous_checkin = checkin
                    previous_spot = await self.spot_service.get_spot_by_id(
                        checkin.spot_id
                    )
                    previous_spot_name = (
                        previous_spot.name if previous_spot else "Неизвестный спот"
                    )
                    # Завершаем существующий чек-ин
                    await self.checkin_repo.deactivate_checkin(checkin.id, update_duration=True)
                    logger.info(
                        f"Завершен активный чек-ин #{checkin.id} типа {checkin.type} для пользователя {user.id} на споте {previous_spot_name}"
                    )
                    await self.notification_service.send_checkout_notification(
                        user, previous_spot_name
                    )
                    await self.notification_service.send_spot_checkout_notification(
                        user, previous_spot_name
                    )
                    break

            # Определение времени активности и планирования
            active_until = (
                now + timedelta(seconds=duration) if checkin_type in [1, 2] else None
            )
            planned_at = (
                now + timedelta(hours=1)
                if checkin_type == 2
                else (now + timedelta(days=1) if checkin_type == 3 else None)
            )

            # Создание нового чек-ина
            checkin = Checkin(
                id=0,  # Автоинкремент
                user_id=user.id,
                spot_id=spot_id,
                type=checkin_type,
                duration=duration,
                created_at=now,
                active_until=active_until,
                planned_at=planned_at,
                active=True,
            )
            checkin_id = await self.checkin_repo.create(checkin)

            # Получение данных для сообщения
            on_spot, planning = await self.get_active_users(spot_id)

            # Отправка уведомления о новом чек-ине
            await self.notification_service.send_checkin_notification(user, spot.name)
            await self.notification_service.send_spot_checkin_notification(
                user, spot.name
            )

            # Формирование сообщения
            hours = duration // 3600
            if previous_checkin:
                message = (
                    f"🚪 Йо, ты покинул '{previous_spot_name}'! ✅ Теперь ты зачекинился на '{spot.name}'! Лови вайб на {hours} ч! 🏄‍♂️\n"
                    f"💨 На споте: {len(on_spot)}\n"
                    f"📅 Планируют подтянуться: {len(planning)}"
                )
            else:
                message = (
                    f"✅ Йо, ты зачекинился на '{spot.name}'! Лови вайб на {hours} ч! 🏄‍♂️\n"
                    f"💨 На споте: {len(on_spot)}\n"
                    f"📅 Планируют подтянуться: {len(planning)}"
                )
            kb = MainKeyboards.get_post_checkin_menu(checkin_id)
            await self.bot.send_message(
                user.id, message, reply_markup=kb, parse_mode="HTML"
            )
            logger.info(
                f"Чек-ин #{checkin_id} создан для пользователя {user.id} на споте id {spot_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Ошибка при создании чек-ина для спота id {spot_id}: {e}")
            await self.bot.send_message(
                user.id, f"😕 Ошибка при чек-ине, бро: {str(e)}"
            )
            return False

    async def get_user_active_checkins(self, user_id: int) -> List[Checkin]:
        """Получение активных чек-инов пользователя."""
        try:
            checkins = await self.checkin_repo.get_by_user(user_id)
            return checkins
        except Exception as e:
            logger.error(f"Ошибка при получении активных чек-инов пользователя {user_id}: {e}")
            return []

    async def get_spot_checkins(self, spot_id: int) -> List[Checkin]:
        """Получение всех чек-инов для спота."""
        try:
            checkins = await self.checkin_repo.get_by_spot(spot_id)
            return checkins
        except Exception as e:
            logger.error(f"Ошибка при получении чек-инов спота {spot_id}: {e}")
            return []

    async def get_active_users(self, spot_id: int) -> Tuple[List[User], List[User]]:
        """Получение активных и планирующих пользователей на споте."""
        try:
            now = datetime.utcnow()
            checkins = await self.checkin_repo.get_by_spot(spot_id)
            on_spot = []
            planning = []
            for checkin in checkins:
                user_data = await self.user_repo.get_by_id(checkin.user_id)
                if not user_data:
                    continue
                user = User(
                    id=checkin.user_id,
                    name=user_data.name,
                    username=user_data.username,
                )
                if (
                    checkin.type == 1
                    and checkin.active_until
                    and now < checkin.active_until
                    and checkin.active
                ):
                    on_spot.append(user)
                elif (
                    checkin.type == 3
                    and checkin.planned_at
                    and now < checkin.planned_at
                    and checkin.active
                ):
                    planning.append(user)
            logger.info(
                f"Найдено {len(on_spot)} активных и {len(planning)} планирующих для спота id {spot_id}"
            )
            return on_spot, planning
        except Exception as e:
            logger.error(
                f"Ошибка при получении пользователей для спота id {spot_id}: {e}"
            )
            return [], []

    async def get_checkin_by_id(self, checkin_id: int) -> Optional[Checkin]:
        """Получение чек-ина по ID."""
        try:
            checkin = await self.checkin_repo.get_by_id(checkin_id)
            if not checkin:
                logger.warning(f"Чек-ин #{checkin_id} не найден")
            return checkin
        except Exception as e:
            logger.error(f"Ошибка при получении чек-ина #{checkin_id}: {e}")
            return None

    async def get_all_active_checkins(self) -> List[Checkin]:
        """Получение всех активных чек-инов."""
        try:
            checkins = await self.checkin_repo.get_active_checkins()
            return checkins
        except Exception as e:
            logger.error(f"Ошибка при получении всех активных чек-инов: {e}")
            return []

    async def deactivate_checkin(self, checkin_id: int, update_duration: bool = False) -> bool:
        """Деактивация чек-ина."""
        try:
            success = await self.checkin_repo.deactivate_checkin(checkin_id, update_duration)
            if success:
                logger.info(f"Чек-ин #{checkin_id} деактивирован")
            else:
                logger.warning(f"Не удалось деактивировать чек-ин #{checkin_id}")
            return success
        except Exception as e:
            logger.error(f"Ошибка при деактивации чек-ина #{checkin_id}: {e}")
            return False

    async def update_checkin_duration(
        self, checkin_id: int, active_until: datetime, duration: int
    ) -> bool:
        """Обновление времени активности и длительности чек-ина."""
        try:
            success = await self.checkin_repo.update_active_until(checkin_id, active_until, duration)
            if success:
                logger.info(f"Чек-ин #{checkin_id} обновлен")
            else:
                logger.warning(f"Не удалось обновить чек-ин #{checkin_id}")
            return success
        except Exception as e:
            logger.error(f"Ошибка при обновлении чек-ина #{checkin_id}: {e}")
            return False
