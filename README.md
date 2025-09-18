# WindSpotBot 🤙

Telegram-бот для кайтсерферов и виндсёрферов. Позволяет находить споты, делать чек-ины, просматривать активность (погода, пользователи, чаты) и общаться в чатах спотов.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![aiogram 3.x](https://img.shields.io/badge/aiogram-3.x-green.svg)](https://docs.aiogram.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-3.x-lightblue.svg)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌊 Основные возможности

- **Чек-ины на спотах** - отмечайтесь на месте, планируйте поездки
- **Поиск ближайших спотов** - находите споты по геолокации
- **Активность на спотах** - смотрите кто сейчас катается, погоду, чаты
- **Планирование поездок** - создавайте планы на будущее
- **Уведомления** - получайте уведомления о чек-инах, сообщениях, погоде
- **Чаты спотов** - общайтесь с другими кайтерами в темах для каждого спота

## 🚀 Быстрый старт

### 1. Клонирование и настройка

```bash
git clone <repo>
cd WindSpotBot
```

### 2. Установка зависимостей

```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Linux/macOS)
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Настройка окружения

Скопируйте `.env.example` в `.env` и заполните значения:

```bash
cp .env.example .env
```

Пример `.env`:
```env
BOT_TOKEN=your_bot_token_here
CHAT_ID=your_chat_id_here
ADMINS=123456789,987654321
NEARBY_SPOTS_LIMIT=5
PLANNED_VISITS_LIMIT=5
MIN_SPOT_DISTANCE_M=300
CHECKIN_CHECK_INTERVAL_MINUTES=5
WEATHER_CHECK_INTERVAL_MINUTES=15
MESSAGE_TTL_DAYS=7
STATS_CACHE_TTL_SECONDS=600
MAX_SUBSCRIPTIONS_PER_USER=10
NOTIFICATION_INTERVAL_SECONDS=60
```

### 4. Инициализация базы данных

```bash
# Применение миграций
alembic upgrade head
```

### 5. Запуск бота

```bash
python -m src.bot
```

## 📱 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Запуск бота, показ главного меню |
| `/checkin` | Чек-ин на споте (выбор спота по геолокации) |
| `/spots` | Список ближайших спотов с расстоянием |
| `/activity` | Активность на спотах (погода, пользователи, чаты) |
| `/add_spot` | Добавление нового спота |
| `/subscribe` | Подписка на уведомления |
| `/create_topic` | Создание темы для спота |
| `/test_notification` | Тест отправки уведомления |
| `/test_chat` | Тест отправки сообщения в тему |

## 🏗️ Архитектура проекта

```
WindSpotBot/
├── src/                    # Исходный код
│   ├── bot.py             # Главный файл бота
│   ├── config/            # Конфигурация и настройки
│   │   ├── config.py      # Основные настройки
│   │   └── topics.py      # Настройки тем
│   ├── handlers/          # Обработчики команд
│   │   ├── start.py       # Команда /start
│   │   ├── checkin.py     # Чек-ины
│   │   ├── activity.py    # Активность на спотах
│   │   ├── main_menu.py   # Главное меню
│   │   └── plans.py       # Планирование
│   ├── services/          # Бизнес-логика
│   │   ├── checkin.py     # Управление чек-инами
│   │   ├── spot.py        # Управление спотами
│   │   ├── geo.py         # Работа с геолокацией
│   │   ├── weather.py     # Данные о погоде
│   │   ├── notification.py # Уведомления
│   │   ├── chat.py        # Чаты спотов
│   │   ├── topic.py       # Темы в Telegram
│   │   ├── scheduler.py   # Планировщик задач
│   │   └── stats.py       # Статистика
│   ├── repositories/      # Работа с базой данных
│   │   ├── user.py        # Пользователи
│   │   ├── spot.py        # Споты
│   │   ├── checkin.py     # Чек-ины
│   │   └── subscription.py # Подписки
│   ├── models/            # Pydantic модели
│   │   ├── user.py        # Модель пользователя
│   │   ├── spot.py        # Модель спота
│   │   ├── checkin.py     # Модель чек-ина
│   │   └── subscription.py # Модель подписки
│   ├── keyboards/         # Клавиатуры Telegram
│   │   └── main.py        # Основные клавиатуры
│   └── database/          # Инициализация БД
│       └── init.py        # Создание базы данных
├── tests/                 # Тесты
│   ├── test_bot.py        # Тесты бота
│   ├── test_checkin.py    # Тесты чек-инов
│   └── test_*.py          # Другие тесты
├── migrations/            # Миграции базы данных
│   └── versions/          # Файлы миграций
├── data/                  # База данных SQLite
├── docs/                  # Документация
│   ├── api.md            # API документация
│   ├── architecture.md   # Архитектура
│   ├── testing.md        # Тестирование
│   └── ux.md             # UX/UI
├── .vscode/              # Настройки VS Code/Cursor
├── .env.example          # Пример конфигурации
├── requirements.txt      # Зависимости Python
├── pyproject.toml        # Конфигурация проекта
├── Makefile             # Команды разработки
└── README.md            # Этот файл
```

## 🛠️ Разработка

### Команды разработки

```bash
# Установка зависимостей
make install

# Запуск тестов
make test

# Форматирование кода
make format

# Проверка стиля кода
make lint

# Запуск бота
make run

# Очистка временных файлов
make clean
```

### Тестирование

```bash
# Запуск всех тестов
pytest tests/ -v

# Запуск с покрытием
pytest tests/ --cov=src --cov-report=html

# Запуск конкретного теста
pytest tests/test_checkin.py -v
```

### Форматирование и линтинг

```bash
# Форматирование кода (Black)
black src/ tests/

# Проверка стиля (Flake8)
flake8 src/ tests/

# Проверка типов (MyPy)
mypy src/
```

## 🗄️ База данных

### Структура таблиц

- **users** - Пользователи (id, name, username, timezone, created_at)
- **spots** - Споты (id, name, latitude, longitude, description, created_by)
- **checkins** - Чек-ины (id, user_id, spot_id, type, duration, created_at, active_until, planned_at, active, planned_date)
- **subscriptions** - Подписки (user_id, spot_name, event_type, created_at)
- **spot_topics** - Темы спотов (spot_name, thread_id)

### Миграции

```bash
# Создание новой миграции
alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `BOT_TOKEN` | Токен бота от @BotFather | - |
| `CHAT_ID` | ID чата для создания тем | - |
| `ADMINS` | Список ID администраторов | - |
| `NEARBY_SPOTS_LIMIT` | Лимит ближайших спотов | 5 |
| `PLANNED_VISITS_LIMIT` | Лимит запланированных поездок | 5 |
| `MIN_SPOT_DISTANCE_M` | Минимальное расстояние до спота (м) | 300 |
| `CHECKIN_CHECK_INTERVAL_MINUTES` | Интервал проверки чек-инов (мин) | 5 |
| `WEATHER_CHECK_INTERVAL_MINUTES` | Интервал проверки погоды (мин) | 15 |
| `MESSAGE_TTL_DAYS` | Время жизни сообщений (дни) | 7 |
| `STATS_CACHE_TTL_SECONDS` | Время кэширования статистики (сек) | 600 |
| `MAX_SUBSCRIPTIONS_PER_USER` | Максимум подписок на пользователя | 10 |
| `NOTIFICATION_INTERVAL_SECONDS` | Интервал уведомлений (сек) | 60 |

## 📚 Документация

- [Архитектура](docs/architecture.md) - Подробное описание архитектуры
- [API](docs/api.md) - API документация
- [Тестирование](docs/testing.md) - Руководство по тестированию
- [UX/UI](docs/ux.md) - Дизайн и пользовательский опыт
- [Руководство разработчика](README_DEVELOPMENT.md) - Полное руководство по разработке

## 🤝 Поддержка

- **Чат проекта**: [@WindSpotChat](https://t.me/WindSpotChat) - темы для спотов
- **Техническая поддержка**: [@WindSpotRU](https://t.me/WindSpotRU)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

## 🚀 Деплой

### Docker

```bash
# Сборка образа
docker build -t windspotbot .

# Запуск контейнера
docker-compose up -d
```

### Переменные окружения для продакшена

Убедитесь, что все необходимые переменные окружения настроены в вашей среде развертывания.

## 🔄 Обновления

Следите за обновлениями в [CHANGELOG.md](CHANGELOG.md).

---

**Создано с ❤️ для кайтсерферов и виндсёрферов** 🤙💨🏄‍♂️