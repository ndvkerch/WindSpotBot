from apscheduler.schedulers.asyncio import AsyncIOScheduler

class SchedulerService:
    """Сервис для планирования задач."""
    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler

    def start(self):
        """Запуск планировщика."""
        # TODO: Реализовать логику
        pass