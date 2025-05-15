from aiogram import Bot
from src.models.checkin import Checkin
from src.models.user import User
from src.models.spot import Spot
from src.repositories.checkin import CheckinRepository
from src.repositories.user import UserRepository
from src.services.notification import NotificationService
from src.services.weather import WeatherService
from src.services.spot import SpotService
from src.keyboards.main import MainKeyboards
from datetime import datetime, timedelta, date
import logging

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

    async def get_all_active_checkins(self) -> list[Checkin]:
        """Получение всех активных чек-инов."""
        try:
            return await self.checkin_repo.get_active_checkins()
        except Exception as e:
            logger.error(f"Ошибка при получении активных чек-инов: {e}")
            return []

    async def create_checkin(
        self,
        user: User,
        spot_id: int,
        checkin_type: int,
        duration: int = 3600,
        planned_hours: int = None,
        planned_date: date = None,
    ) -> bool:
        """Создание нового чек-ина."""
        try:
            spot = await self.spot_service.get_spot_by_id(spot_id)
            if not spot:
                await self.bot.send_message(
                    user.id, f"🤙 Спот с ID {spot_id} не найден, бро! 😕"
                )
                logger.warning(f"Спот с ID {spot_id} не найден для чек-ина")
                return False

            now = datetime.utcnow()
            checkins = await self.checkin_repo.get_by_user(user.id)
            previous_checkin = None
            previous_spot_name = None
            for checkin in checkins:
                if (
                    checkin.active_until
                    and now < checkin.active_until
                    and checkin.active
                    and checkin.type in (1, 2)  # Тип 3 не конфликтует
                ):
                    previous_checkin = checkin
                    previous_spot = await self.spot_service.get_spot_by_id(
                        checkin.spot_id
                    )
                    previous_spot_name = (
                        previous_spot.name if previous_spot else "Неизвестный спот"
                    )
                    if checkin.type == 2:
                        # Удаляем активный чек-ин 2-го типа
                        await self.delete_checkin(checkin.id, user)
                    else:
                        # Деактивируем чек-ин 1-го типа
                        await self.checkin_repo.deactivate_checkin(
                            checkin.id, update_duration=True
                        )
                        await self.notification_service.send_checkout_notification(
                            user, previous_spot_name
                        )
                        await self.notification_service.send_spot_checkout_notification(
                            user, previous_spot_name, checkin.type
                        )
                    break

            created_at = now
            active_until = None
            planned_at = None
            if checkin_type == 1:
                duration = duration or 3600
                active_until = now + timedelta(seconds=duration)
            elif checkin_type == 2 and planned_hours:
                duration = duration or 3600
                planned_at = now + timedelta(hours=planned_hours)
                active_until = planned_at + timedelta(seconds=duration)
            elif checkin_type == 3 and planned_date:
                # active_until = конец дня planned_date (23:59:59)
                active_until = datetime.combine(planned_date, datetime.max.time())
                duration = 0  # Для типа 3 duration не используется, устанавливаем 0

            checkin = Checkin(
                id=0,
                user_id=user.id,
                spot_id=spot_id,
                type=checkin_type,
                duration=duration,
                created_at=created_at,
                active_until=active_until,
                planned_at=planned_at,
                planned_date=planned_date,
                active=True,
            )
            checkin_id = await self.checkin_repo.create(checkin)
            if not checkin_id:
                logger.error(f"Не удалось создать чек-ин для пользователя {user.id}")
                return False

            # Уведомление о чек-ине только для типа 1
            if checkin_type == 1:
                await self.notification_service.send_checkin_notification(user, spot.name)
            await self.notification_service.send_spot_checkin_notification(
                user, spot.name, checkin_type, duration, planned_hours, planned_date
            )

            if checkin_type == 2:
                await self.bot.send_message(
                    user.id,
                    f"📅 Йо, ты запланировал тусу на '{spot.name}' через {planned_hours} ч! "
                    f"Не забудь отметить, когда будешь на месте! 🏄‍♂️",
                    reply_markup=MainKeyboards.get_confirm_arrival_menu(checkin_id),
                )
            elif checkin_type == 3:
                pass  # Убрано дублирующее сообщение, оно отправляется в handler
            else:
                weather = await self.weather_service.get_weather(
                    spot.latitude, spot.longitude
                )
                wind_speed = weather.get("wind_speed", "N/A")
                await self.bot.send_message(
                    user.id,
                    (
                        f"✅ Йо, ты зачекинился на '{spot.name}'! 🏄‍♂️\n"
                        f"Ветер: {wind_speed} м/с. Лови волну! 💨"
                    ),
                    reply_markup=MainKeyboards.get_post_checkin_menu(checkin_id),
                )

            logger.info(
                f"Чек-ин #{checkin_id} (тип {checkin_type}) создан для пользователя {user.id} на споте '{spot.name}'"
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка при создании чек-ина для пользователя {user.id}: {e}")
            return False

    async def deactivate_checkin(self, checkin_id: int, update_duration: bool = False) -> bool:
        """Деактивация чек-ина."""
        try:
            checkin = await self.checkin_repo.get_by_id(checkin_id)
            if not checkin:
                logger.warning(f"Чек-ин #{checkin_id} не найден")
                return False

            spot = await self.spot_service.get_spot_by_id(checkin.spot_id)
            spot_name = spot.name if spot else "Неизвестный спот"

            success = await self.checkin_repo.deactivate_checkin(checkin_id, update_duration)
            if success:
                user = await self.user_repo.get_by_id(checkin.user_id)
                if user:
                    user_model = User(id=user.id, name=user.name, username=user.username)
                    await self.notification_service.send_checkout_notification(user_model, spot_name)
                    await self.notification_service.send_spot_checkout_notification(
                        user_model, spot_name, checkin.type
                    )
                logger.info(f"Чек-ин #{checkin_id} деактивирован")
                return True
            else:
                logger.warning(f"Не удалось деактивировать чек-ин #{checkin_id}")
                return False
        except Exception as e:
            logger.error(f"Ошибка при деактивации чек-ина #{checkin_id}: {e}")
            return False

    async def delete_checkin(self, checkin_id: int, user: User) -> bool:
        """Удаление чек-ина из базы."""
        try:
            checkin = await self.checkin_repo.get_by_id(checkin_id)
            if not checkin:
                logger.warning(f"Чек-ин #{checkin_id} не найден")
                return False

            spot = await self.spot_service.get_spot_by_id(checkin.spot_id)
            spot_name = spot.name if spot else "Неизвестный спот"

            async with self.checkin_repo.db.execute(
                "DELETE FROM checkins WHERE id = ?", (checkin_id,)
            ) as cursor:
                await self.checkin_repo.db.commit()
                if cursor.rowcount == 0:
                    logger.warning(f"Не удалось удалить чек-ин #{checkin_id}")
                    return False

            await self.notification_service.send_checkout_notification(user, spot_name)
            await self.notification_service.send_spot_checkout_notification(
                user, spot_name, checkin.type
            )

            logger.info(f"Чек-ин #{checkin_id} удален для пользователя {user.id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при удалении чек-ина #{checkin_id}: {e}")
            return False

    async def cancel_planned_checkin(self, checkin_id: int, user: User) -> bool:
        """Отмена чек-ина типа 3."""
        try:
            checkin = await self.checkin_repo.get_by_id(checkin_id)
            if not checkin or checkin.type != 3:
                logger.warning(f"Чек-ин #{checkin_id} не найден или не типа 3")
                return False

            success = await self.delete_checkin(checkin_id, user)
            return success
        except Exception as e:
            logger.error(f"Ошибка при отмене чек-ина #{checkin_id}: {e}")
            return False

    async def send_planned_checkin_reminders(self, current_date: date):
        """Отправка напоминаний для чек-инов типа 3 на текущую дату."""
        try:
            checkins = await self.checkin_repo.get_todays_planned_checkins(current_date)
            for checkin in checkins:
                user = await self.user_repo.get_by_id(checkin.user_id)
                spot = await self.spot_service.get_spot_by_id(checkin.spot_id)
                if user and spot:
                    user_model = User(id=user.id, name=user.name, username=user.username)
                    await self.bot.send_message(
                        user_model.id,
                        f"📅 Йо, ты запланировал посетить '{spot.name}' сегодня! Подтверди намерения: 🏄‍♂️",
                        reply_markup=MainKeyboards.get_planned_checkin_reminder_menu(checkin.id),
                    )
                    logger.info(f"Напоминание отправлено для чек-ина #{checkin.id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке напоминаний на {current_date}: {e}")

    async def update_checkin_duration(self, checkin_id: int, active_until: datetime, duration: int) -> bool:
        """Обновление времени действия и длительности чек-ина."""
        try:
            success = await self.checkin_repo.update_active_until(checkin_id, active_until, duration)
            if success:
                logger.info(
                    f"Чек-ин #{checkin_id} обновлен: active_until={active_until}, duration={duration}"
                )
                return True
            else:
                logger.warning(f"Не удалось обновить чек-ин #{checkin_id}")
                return False
        except Exception as e:
            logger.error(f"Ошибка при обновлении чек-ина #{checkin_id}: {e}")
            return False

    async def confirm_arrival(self, checkin_id: int, user: User, duration: int = 3600) -> bool:
        """Подтверждение прибытия для чек-ина 2-го типа, преобразование в чек-ин 1-го типа."""
        try:
            checkin = await self.checkin_repo.get_by_id(checkin_id)
            if not checkin or checkin.type != 2 or not checkin.active:
                logger.warning(
                    f"Чек-ин #{checkin_id} не найден, не типа 2 или не активен"
                )
                await self.bot.send_message(
                    user.id, "😕 Чек-ин не найден или уже неактивен, бро!"
                )
                return False

            spot = await self.spot_service.get_spot_by_id(checkin.spot_id)
            if not spot:
                logger.warning(f"Спот с ID {checkin.spot_id} не найден")
                await self.bot.send_message(
                    user.id, f"🤙 Спот с ID {checkin.spot_id} не найден, бро! 😕"
                )
                return False

            now = datetime.utcnow()
            async with self.checkin_repo.db.execute(
                "UPDATE checkins SET type = ?, created_at = ?, active_until = ?, duration = ?, planned_at = ? WHERE id = ?",
                (
                    1,
                    now.isoformat(),
                    (now + timedelta(seconds=duration)).isoformat(),
                    duration,
                    None,
                    checkin_id,
                ),
            ) as cursor:
                await self.checkin_repo.db.commit()
                if cursor.rowcount == 0:
                    logger.warning(f"Не удалось обновить чек-ин #{checkin_id}")
                    return False

            await self.notification_service.send_checkin_notification(user, spot.name)
            await self.notification_service.send_spot_checkin_notification(
                user, spot.name, checkin_type=1, duration=duration
            )

            weather = await self.weather_service.get_weather(spot.latitude, spot.longitude)
            wind_speed = weather.get("wind_speed", "N/A")
            await self.bot.send_message(
                user.id,
                (
                    f"✅ Йо, ты на '{spot.name}'! 🏄‍♂️\n"
                    f"Ветер: {wind_speed} м/с. Лови волну! 💨"
                ),
                reply_markup=MainKeyboards.get_post_checkin_menu(checkin_id),
            )

            logger.info(
                f"Чек-ин #{checkin_id} преобразован из типа 2 в тип 1 для пользователя {user.id}"
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка при подтверждении прибытия для чек-ина #{checkin_id}: {e}")
            await self.bot.send_message(
                user.id, f"😕 Ошибка при подтверждении прибытия: {str(e)}"
            )
            return False
