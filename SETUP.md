# Настройка WindSpotBot 🚀

Этот файл содержит пошаговые инструкции по настройке WindSpotBot для разработки и продакшена.

## 📋 Предварительные требования

- Python 3.8+
- Git
- Telegram Bot Token
- Telegram Chat ID (для создания тем)

## 🛠️ Быстрая настройка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd WindSpotBot
```

### 2. Создание виртуального окружения

```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Linux/macOS)
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка конфигурации

Создайте файл `.env` в корне проекта:

```env
# Обязательные параметры
BOT_TOKEN=your_bot_token_here
CHAT_ID=your_chat_id_here
ADMINS=123456789,987654321

# Настройки спотов
NEARBY_SPOTS_LIMIT=5
PLANNED_VISITS_LIMIT=5
MIN_SPOT_DISTANCE_M=300

# Интервалы проверки (в минутах)
CHECKIN_CHECK_INTERVAL_MINUTES=5
WEATHER_CHECK_INTERVAL_MINUTES=15

# Настройки сообщений
MESSAGE_TTL_DAYS=7
STATS_CACHE_TTL_SECONDS=600

# Настройки подписок
MAX_SUBSCRIPTIONS_PER_USER=10
NOTIFICATION_INTERVAL_SECONDS=60
```

### 5. Инициализация базы данных

```bash
# Применение миграций
alembic upgrade head
```

### 6. Запуск бота

```bash
# Запуск в режиме разработки
python -m src.bot

# Или через Makefile
make run
```

## 🔧 Получение необходимых данных

### Telegram Bot Token

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Введите имя бота (например: "WindSpotBot")
4. Введите username бота (например: "windspotbot")
5. Скопируйте полученный токен

### Telegram Chat ID

1. Добавьте бота в группу или канал
2. Отправьте любое сообщение в группу
3. Перейдите по ссылке: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Найдите `chat.id` в ответе (например: `-1001234567890`)

### Admin IDs

1. Отправьте боту команду `/start`
2. Перейдите по ссылке: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Найдите `from.id` в ответе (например: `123456789`)

## 🐳 Настройка с Docker

### 1. Создание .env файла

```env
BOT_TOKEN=your_bot_token_here
CHAT_ID=your_chat_id_here
ADMINS=123456789,987654321
```

### 2. Запуск с Docker Compose

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f windspotbot

# Остановка
docker-compose down
```

## 🔧 Настройка для разработки

### 1. Установка дополнительных зависимостей

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock
pip install black flake8 mypy
```

### 2. Настройка IDE

#### Cursor/VS Code
Проект уже настроен с:
- Автоматическим форматированием (Black)
- Проверкой стиля (Flake8)
- Поддержкой тестирования (pytest)
- Конфигурацией запуска и отладки

#### PyCharm
1. Откройте проект в PyCharm
2. Настройте интерпретатор Python
3. Установите плагины для Black и Flake8

### 3. Запуск тестов

```bash
# Запуск всех тестов
pytest tests/ -v

# Запуск с покрытием
pytest tests/ --cov=src --cov-report=html

# Запуск конкретного теста
pytest tests/test_checkin.py -v
```

### 4. Форматирование кода

```bash
# Форматирование кода
black src/ tests/

# Проверка стиля
flake8 src/ tests/

# Проверка типов
mypy src/
```

## 🚀 Настройка для продакшена

### 1. Переменные окружения

```env
# Продакшен настройки
BOT_TOKEN=your_production_bot_token
CHAT_ID=your_production_chat_id
ADMINS=123456789,987654321

# Оптимизированные настройки
NEARBY_SPOTS_LIMIT=10
PLANNED_VISITS_LIMIT=10
MIN_SPOT_DISTANCE_M=500
CHECKIN_CHECK_INTERVAL_MINUTES=2
WEATHER_CHECK_INTERVAL_MINUTES=10
MESSAGE_TTL_DAYS=30
STATS_CACHE_TTL_SECONDS=300
MAX_SUBSCRIPTIONS_PER_USER=20
NOTIFICATION_INTERVAL_SECONDS=30

# Продакшен настройки
DEBUG=false
LOG_LEVEL=INFO
```

### 2. Системный сервис (systemd)

Создайте файл `/etc/systemd/system/windspotbot.service`:

```ini
[Unit]
Description=WindSpotBot
After=network.target

[Service]
Type=simple
User=windspotbot
WorkingDirectory=/opt/windspotbot
ExecStart=/opt/windspotbot/venv/bin/python -m src.bot
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/windspotbot

[Install]
WantedBy=multi-user.target
```

Установка сервиса:

```bash
# Копирование файла сервиса
sudo cp windspotbot.service /etc/systemd/system/

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable windspotbot

# Запуск сервиса
sudo systemctl start windspotbot

# Проверка статуса
sudo systemctl status windspotbot
```

## 🔍 Проверка настройки

### 1. Проверка зависимостей

```bash
python -c "import aiogram, aiosqlite, pydantic; print('Все зависимости установлены')"
```

### 2. Проверка конфигурации

```bash
python -c "from src.config.config import settings; print(f'Bot token: {settings.BOT_TOKEN[:10]}...')"
```

### 3. Проверка базы данных

```bash
# Проверка миграций
alembic current

# Проверка таблиц
sqlite3 data/database.db ".tables"
```

### 4. Проверка бота

```bash
# Запуск в тестовом режиме
python -m src.bot
```

## 🐛 Решение проблем

### Ошибка импорта модулей

```bash
# Проблема
ModuleNotFoundError: No module named 'src'

# Решение
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Или
python -m src.bot
```

### Ошибка подключения к базе данных

```bash
# Проблема
sqlite3.OperationalError: database is locked

# Решение
# Проверьте, что база данных не используется другим процессом
# Убедитесь, что все соединения закрыты
```

### Ошибка аутентификации бота

```bash
# Проблема
aiogram.exceptions.TelegramUnauthorizedError: Unauthorized

# Решение
# Проверьте BOT_TOKEN в .env
# Убедитесь, что токен действителен
```

### Ошибка миграций

```bash
# Проблема
alembic.util.exc.CommandError: Can't locate revision identified by 'head'

# Решение
# Сброс миграций
alembic stamp head
# Или создание новой миграции
alembic revision --autogenerate -m "Initial migration"
```

## 📚 Дополнительные ресурсы

- [Руководство по разработке](README_DEVELOPMENT.md)
- [Архитектура проекта](docs/architecture.md)
- [API документация](docs/api.md)
- [Тестирование](docs/testing.md)
- [UX/UI](docs/ux.md)

## 🤝 Поддержка

- **Техническая поддержка**: [@WindSpotRU](https://t.me/WindSpotRU)
- **Чат проекта**: [@WindSpotChat](https://t.me/WindSpotChat)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)

---

**Создано с ❤️ для кайтсерферов и виндсёрферов** 🤙💨🏄‍♂️



