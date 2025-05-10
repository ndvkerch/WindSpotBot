# WindSpotBot

Telegram-бот для кайтсерферов и виндсёрферов. Позволяет находить споты, делать чек-ины, просматривать активность (погода, пользователи, чаты) и общаться в чатах спотов.

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone <repo>
   cd windspotbot
   ```

2. Создайте и активируйте виртуальную среду:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Настройте `.env`:
   ```bash
   cp .env.example .env
   ```
   Пример `.env`:
   ```
   BOT_TOKEN=your_bot_token
   CHAT_ID=your_chat_id
   MIN_SPOT_DISTANCE_M=300
   NEARBY_SPOTS_LIMIT=5
   STATS_CACHE_TTL_SECONDS=3600
   ```

## Запуск

```bash
python -m src.bot
```

## Команды

- `/start`: Запуск бота, показ главного меню.
- `/checkin`: Чек-ин на споте (выбор спота по геолокации, выбор типа: на месте/планирую).
- `/spots`: Список ближайших спотов с расстоянием.
- `/activity`: Активность на спотах (погода: ветер, температура воды; пользователи: на месте/планируют; ссылки на чаты).
- `/add_spot`: Добавление нового спота (название, геолокация, описание).
- `/subscribe`: Подписка на уведомления (чек-ины, сообщения, погода).
- `/create_topic`: Создание темы для спота.
- `/test_notification`: Тест отправки уведомления.
- `/test_chat`: Тест отправки сообщения в тему.

## Структура проекта

```
src/
├── bot.py              # Главный файл бота
├── config/            # Конфигурация (.env, config.py)
├── handlers/          # Обработчики команд (планируется вынос)
├── keyboards/         # Клавиатуры (main.py)
├── models/            # Pydantic-модели (Spot, SpotWithDistance, User и др.)
├── repositories/      # Репозитории для работы с БД
├── services/          # Бизнес-логика (SpotService, CheckinService и др.)
└── data/              # База данных (database.db)
```

## Разработка

- Используйте ветку `dev` для разработки.
- Коммиты на русском языке.
- Тестирование: Запуск `pytest` (см. `docs/testing.md`).

## Поддержка

- Чат: `@WindSpotChat` (темы для спотов).
- Техническая поддержка: `@WindSpotRU`.

## Деактивация виртуальной среды

```bash
deactivate
```