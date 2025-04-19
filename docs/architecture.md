# Архитектура WindSpotBot

Проект использует модульную архитектуру с изолированными сервисами и репозиториями.

## Структура
- `handlers/`: Обработчики команд и callback'ов (`/start`, чек-ины).
- `services/`: Бизнес-логика:
  - `CheckinService`: Управление чек-инами.
  - `SpotService`: Поиск и кэширование спотов.
  - `NotificationService`: Отправка уведомлений в темы спотов.
  - `ChatService`: Получение сообщений из тем спотов.
  - `RatingService`: Оценка спотов.
  - `WeatherService`: Получение погоды.
  - `SchedulerService`: Планировщик задач.
  - `StatsService`: Статистика.
- `repositories/`: Работа с БД:
  - `UserRepository`: Пользователи.
  - `SpotRepository`: Споты.
  - `CheckinRepository`: Чек-ины.
- `models/`: Pydantic-модели (`User`, `Spot`, `Checkin`).
- `keyboards/`: Клавиатуры (`main.py`).
- `config/`: Конфигурация (`config.py`, `topics.py`).

## Схема взаимодействия
Handlers -> Services -> Repositories -> SQLite
- Handlers обрабатывают команды и вызывают сервисы.
- Сервисы содержат бизнес-логику и используют репозитории.
- Репозитории выполняют SQL-запросы к SQLite.

## Чат спотов
- Используются Telegram Topics в @WindSpotChat вместо хэштегов.
- Каждая тема соответствует споту (например, «Должанка»).
- Уведомления отправляются в тему с помощью `message_thread_id`.
- Хранилище: Таблица `spot_topics` в SQLite или `config/topics.py`.
- @WindSpotRU используется для технической поддержки.
