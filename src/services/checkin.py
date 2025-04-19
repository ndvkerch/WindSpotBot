from repositories.checkin import CheckinRepository
from services.spot import SpotService

class CheckinService:
    """Сервис для управления чек-инами."""
    def __init__(self, checkin_repo: CheckinRepository, spot_service: SpotService):
        self.checkin_repo = checkin_repo
        self.spot_service = spot_service

    async def create_checkin(self, user_id: int, spot_id: int, checkin_type: int, duration: int) -> int:
        """Создание чек-ина."""
        # TODO: Реализовать логику
        checkin_id = await self.checkin_repo.create(user_id, spot_id, checkin_type, duration)
        await self.spot_service.invalidate_spot_cache(lat=None, lon=None)
        return checkin_id