# Архитектура WindSpotBot

Проект использует модульную архитектуру с изолированными сервисами и репозиториями, что обеспечивает независимость бизнес-логики от хендлеров и удобство тестирования.

## Структура

- `handlers/`: Обработчики команд и callback'ов (`/start`, `/checkin`, `/spots`, `/activity`, `/add_spot`). Планируется вынос из `bot.py` в отдельные модули.
- `services/`: Бизнес-логика:
  - `CheckinService`: Управление чек-инами (создание, получение активных пользователей).
  - `SpotService`: Управление спотами (поиск, добавление, кэширование).
  - `GeoService`: Работа с геолокацией (расчёт расстояний, кэширование координат).
  - `NotificationService`: Отправка уведомлений подписчикам (чек-ины, сообщения, погода).
  - `ChatService`: Отправка/получение сообщений в темах спотов, создание тем.
  - `TopicService`: Управление темами в Telegram.
  - `WeatherService`: Получение данных о погоде через API Open-Meteo (wind_speed_10m, water_temperature).
  - `SubscriptionService`: Управление подписками (в разработке).
  - `RatingService`: Оценка спотов (планируется).
  - `SchedulerService`: Планировщик задач (планируется).
  - `StatsService`: Статистика активности (планируется).
- `repositories/`: Работа с базой данных:
  - `UserRepository`: Пользователи.
  - `SpotRepository`: Споты.
  - `CheckinRepository`: Чек-ины (создание, получение по пользователю и споту).
  - `SubscriptionRepository`: Подписки.
- `models/`: Pydantic-модели:
  - `User`: Пользователь.
  - `Spot`: Спот.
  - `SpotWithDistance`: Спот с расстоянием до пользователя.
  - `Checkin`: Чек-ин.
  - `Subscription`: Подписка.
- `keyboards/`: Клавиатуры:
  - `main.py`: Главное меню, списки спотов, типы чек-инов.
- `config/`: Конфигурация:
  - `config.py`: Загрузка `.env`.
  - `topics.py`: Настройки тем (если используется).

## Схема взаимодействия

```
Handlers -> Services -> Repositories -> SQLite (data/database.db)
```

- **Хендлеры**: Обрабатывают команды и callback'ы, вызывая сервисы. Не содержат бизнес-логики.
- **Сервисы**: Реализуют бизнес-логику, взаимодействуют с репозиториями и внешними API (например, Open-Meteo).
- **Репозитории**: Инкапсулируют работу с базой данных SQLite (`data/database.db`).

## Чат спотов

- Темы в Telegram-группе `@WindSpotChat` для каждого спота.
- `ChatService`: Отправка/получение сообщений, создание тем при первом сообщении.
- `NotificationService`: Уведомления подписчикам о чек-инах, сообщениях, погоде.
- Хранилище:
  - Таблица `spot_topics`: Связь спотов и тем.
  - Таблица `subscriptions`: Подписки пользователей.
- Техническая поддержка: `@WindSpotRU`.

## База данных

- SQLite: `data/database.db`.
- Таблицы:
  - `users`: Пользователи (id, username, created_at).
  - `spots`: Споты (id, name, latitude, longitude, description, created_by).
  - `checkins`: Чек-ины (id, user_id, spot_id, type, duration, created_at, active_until, planned_at).
  - `subscriptions`: Подписки (user_id, spot_id, created_at).
  - `spot_topics`: Темы спотов (spot_name, thread_id).

## Конфигурация

- Файл `.env`:
  ```
  BOT_TOKEN=your_bot_token
  CHAT_ID=your_chat_id
  MIN_SPOT_DISTANCE_M=300
  NEARBY_SPOTS_LIMIT=5
  STATS_CACHE_TTL_SECONDS=3600
  ```
- Загружается через `config.py` с использованием `pydantic_settings`.