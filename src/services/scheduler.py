from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.services.checkin import CheckinService
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SchedulerService:
    """Сервис для планирования задач."""

    def __init__(self, scheduler: AsyncIOScheduler, checkin_service: CheckinService):
        self.scheduler = scheduler
        self.checkin_service = checkin_service

    def start(self):
        """Запуск планировщика."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Планировщик запущен")

    def add_checkin_expiration_job(self, interval_minutes: int = 5):
        """Добавление задачи для проверки истекших чек-инов."""
        async def check_expired_checkins():
            try:
                active_checkins = await self.checkin_service.get_all_active_checkins()
                now = datetime.utcnow()
                for checkin in active_checkins:
                    if checkin.active_until and now >= checkin.active_until:
                        success = await self.checkin_service.deactivate_checkin(checkin.id, update_duration=False)
                        if success:
                            spot = await self.checkin_service.spot_service.get_spot_by_id(checkin.spot_id)
                            user = await self.checkin_service.user_repo.get_by_id(checkin.user_id)
                            if spot and user:
                                user_model = User(id=user.id, name=user.name, username=user.username)
                                await self.checkin_service.notification_service.send_checkout_notification(
                                    user_model, spot.name
                                )
                                await self.checkin_service.notification_service.send_spot_checkout_notification(
                                    user_model, spot.name
                                )
                            logger.info(f"Чек-ин #{checkin.id} автоматически деактивирован")
                        else:
                            logger.warning(f"Не удалось деактивировать чек-ин #{checkin.id}")
            except Exception as e:
                logger.error(f"Ошибка в задаче проверки чек-инов: {e}")

        self.scheduler.add_job(
            check_expired_checkins,
            'interval',
            minutes=interval_minutes,
            id='check_expired_checkins',
            replace_existing=True
        )
        logger.info(f"Задача проверки чек-инов добавлена с интервалом {interval_minutes} минут")

    def add_checkin_warning_job(self, interval_minutes: int = 2):
        """Добавление задачи предупреждения о скором истечении чек-инов."""
        async def warn_expiring_checkins():
            try:
                now = datetime.utcnow()
                warning_window = now + timedelta(minutes=10)
                checkins = await self.checkin_service.checkin_repo.get_active_checkins()
                for checkin in checkins:
                    if checkin.active_until and now <= checkin.active_until <= warning_window:
                        user = await self.checkin_service.user_repo.get_by_id(checkin.user_id)
                        spot = await self.checkin_service.spot_service.get_spot_by_id(checkin.spot_id)
                        if user and spot:
                            user_model = User(id=user.id, name=user.name, username=user.username)
                            await self.checkin_service.bot.send_message(
                                user_model.id,
                                f"🤙 Йо, твой чек-ин на '{spot.name}' истекает через 5–10 минут! Продлить на час? 💨",
                                reply_markup=MainKeyboards.get_extend_checkin_menu(checkin.id),
                            )
            except Exception as e:
                logger.error(f"Ошибка при отправке предупреждений о чек-инах: {e}")

        self.scheduler.add_job(
            warn_expiring_checkins,
            'interval',
            minutes=interval_minutes,
            id='warn_expiring_checkins',
            replace_existing=True
        )
        logger.info(f"Задача предупреждения о чек-инах добавлена с интервалом {interval_minutes} минут")
