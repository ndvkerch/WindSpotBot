# Архитектура WindSpotBot

Проект использует модульную архитектуру с изолированными сервисами и репозиториями.

## Структура
- `handlers/`: Обработчики команд и callback'ов (`/start`, чек-ины).
- `services/`: Бизнес-логика:
  - `CheckinService`: Управление чек-инами.
  - `SpotService`: Поиск и кэширование спотов.
  - `NotificationService`: Отправка пуш-уведомлений подписчикам.
  - `ChatService`: Отправка и получение сообщений в темах спотов.
  - `TopicService`: Создание и управление темами.
  - `RatingService`: Оценка спотов.
  - `WeatherService`: Получение погоды.
  - `SchedulerService`: Планировщик задач.
  - `StatsService`: Статистика.
- `repositories/`: Работа с БД:
  - `UserRepository`: Пользователи.
  - `SpotRepository`: Споты.
  - `CheckinRepository`: Чек-ины.
  - `SubscriptionRepository`: Подписки.
- `models/`: Pydantic-модели (`User`, `Spot`, `Checkin`, `Subscription`).
- `keyboards/`: Клавиатуры (`main.py`).
- `config/`: Конфигурация (`config.py`, `topics.py`).

## Схема взаимодействия
Handlers -> Services -> Repositories -> SQLite
- Handlers обрабатывают команды и вызывают сервисы.
- Сервисы содержат бизнес-логику и используют репозитории.
- Репозитории выполняют SQL-запросы к SQLite.

## Чат спотов
- Telegram Topics в @WindSpotChat.
- Каждая тема соответствует споту.
- `ChatService`: Отправка/получение сообщений, создание тем при первом сообщении.
- `NotificationService`: Пуши подписчикам (чек-ины, сообщения, погода).
- Хранилище: `spot_topics`, `subscriptions` в `data/database.db`.
- @WindSpotRU: Техническая поддержка.
