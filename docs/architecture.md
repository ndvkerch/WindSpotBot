# Архитектура WindSpotBot
Проект использует модульную архитектуру с изолированными сервисами и репозиториями.
## Структура
- `handlers/`: Обработчики команд и callback'ов (`/start`, чек-ины).
- `services/`: Бизнес-логика:
  - `CheckinService`: Управление чек-инами.
  - `SpotService`: Поиск и кэширование спотов.
  - `NotificationService`: Отправка уведомлений.
  - `ChatService`: Фильтрация сообщений по хэштегам.
  - `RatingService`: Оценка спотов.
  - `WeatherService`: Получение погоды.
  - `SchedulerService`: Планировщик задач.
  - `StatsService`: Статистика.
- `repositories/`: Работа с БД:
  - `UserRepository`: Пользователи.
  - `SpotRepository`: Споты.
  - `CheckinRepository`: Чек-ины.
- `models/`: Pydantic-модели (`User`, `Spot`, `Checkin`).

## Схема взаимодействия
Handlers -> Services -> Repositories -> SQLite
- Handlers обрабатывают команды и вызывают сервисы.
- Сервисы содержат бизнес-логику и используют репозитории.
- Репозитории выполняют SQL-запросы к SQLite.