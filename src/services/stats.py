from repositories.user import UserRepository
from repositories.spot import SpotRepository

class StatsService:
    """Сервис для статистики."""
    def __init__(self, user_repo: UserRepository, spot_repo: SpotRepository):
        self.user_repo = user_repo
        self.spot_repo = spot_repo

    async def get_top_spots(self, limit: int) -> List[dict]:
        """Получение топ-спотов."""
        # TODO: Реализовать логику
        return []