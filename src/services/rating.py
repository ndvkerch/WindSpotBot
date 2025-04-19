from repositories.spot import SpotRepository


class RatingService:
    """Сервис для управления оценками спотов."""

    def __init__(self, spot_repo: SpotRepository):
        self.spot_repo = spot_repo

    async def rate_spot(self, user_id: int, spot_id: int, rating: int):
        """Оценка спота."""
        # TODO: Реализовать логику
        pass
