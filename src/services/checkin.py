from aiogram import Bot
from src.models.checkin import Checkin
from src.repositories.checkin import CheckinRepository
from src.repositories.user import UserRepository
from src.services.notification import NotificationService
from src.services.spot import SpotService
from src.models.user import User
from datetime import datetime, timedelta
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
    ):
        self.bot = bot
        self.checkin_repo = checkin_repo
        self.notification_service = notification_service
        self.spot_service = spot_service
        self.user_repo = user_repo

    async def create_checkin(
        self, user: User, spot_id: int, checkin_type: int, duration: int = 3600
    ) -> bool:
        """Создание чек-ина."""
        try:
            spot = await self.spot_service.get_spot_by_id(spot_id)
            if not spot:
                logger.error(f"Спот с id {spot_id} не найден")
                return False

            now = datetime.utcnow()
            active_until = (
                now + timedelta(seconds=duration) if checkin_type in [1, 2] else None
            )
            planned_at = (
                now + timedelta(hours=1)
                if checkin_type == 2
                else (now + timedelta(days=1) if checkin_type == 3 else None)
            )

            checkin = Checkin(
                id=0,  # Автоинкремент
                user_id=user.id,
                spot_id=spot_id,
                type=checkin_type,
                duration=duration,
                created_at=now,
                active_until=active_until,
                planned_at=planned_at,
            )
            checkin_id = await self.checkin_repo.create(checkin)
            await self.notification_service.send_checkin_notification(user, spot.name)
            logger.info(
                f"Чек-ин #{checkin_id} создан для пользователя {user.id} на споте id {spot_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка при создании чек-ина для спота id {spot_id}: {e}")
            return False

    async def get_active_users(self, spot_id: int) -> tuple[list[User], list[User]]:
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
                ):
                    on_spot.append(user)
                elif (
                    checkin.type == 3
                    and checkin.planned_at
                    and now < checkin.planned_at
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
