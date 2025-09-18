# WindSpotBot - Полное руководство по разработке 🚀

Этот документ содержит исчерпывающее руководство по разработке WindSpotBot - Telegram-бота для кайтсерферов и виндсёрферов.

## 📋 Содержание

- [Быстрый старт](#-быстрый-старт)
- [Настройка окружения](#-настройка-окружения)
- [Структура проекта](#-структура-проекта)
- [Архитектура](#-архитектура)
- [Команды разработки](#-команды-разработки)
- [Тестирование](#-тестирование)
- [База данных](#-база-данных)
- [Разработка новых функций](#-разработка-новых-функций)
- [Отладка и логирование](#-отладка-и-логирование)
- [Деплой](#-деплой)
- [Лучшие практики](#-лучшие-практики)
- [Troubleshooting](#-troubleshooting)

## 🚀 Быстрый старт

### 1. Клонирование и настройка

```bash
# Клонирование репозитория
git clone <repo>
cd WindSpotBot

# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Linux/macOS)
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
# Копирование примера конфигурации
cp .env.example .env

# Редактирование конфигурации
# Заполните BOT_TOKEN, CHAT_ID, ADMINS
```

### 3. Инициализация базы данных

```bash
# Применение миграций
alembic upgrade head
```

### 4. Запуск бота

```bash
# Запуск в режиме разработки
python -m src.bot

# Или через Makefile
make run
```

## 🛠️ Настройка окружения

### Системные требования

- **Python**: 3.8+
- **ОС**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **RAM**: минимум 512MB, рекомендуется 1GB+
- **Диск**: минимум 100MB свободного места

### Установка Python

#### Windows
1. Скачайте Python с [python.org](https://www.python.org/downloads/)
2. Установите с опцией "Add Python to PATH"
3. Проверьте установку: `python --version`

#### macOS
```bash
# Через Homebrew
brew install python@3.11

# Или скачайте с python.org
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip
```

### Настройка IDE

#### Cursor (рекомендуется)
Проект уже настроен для Cursor с:
- Автоматическим форматированием (Black)
- Проверкой стиля (Flake8)
- Поддержкой тестирования (pytest)
- Конфигурацией запуска и отладки

#### VS Code
```bash
# Установка расширений
code --install-extension ms-python.python
code --install-extension ms-python.flake8
code --install-extension ms-python.black-formatter
```

#### PyCharm
1. Откройте проект в PyCharm
2. Настройте интерпретатор Python
3. Установите плагины для Black и Flake8

### Переменные окружения

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

## 📁 Структура проекта

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
│   │   ├── stats.py       # Статистика
│   │   └── rating.py      # Оценка спотов
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
└── README.md            # Основной README
```

## 🏗️ Архитектура

### Принципы архитектуры

1. **Разделение ответственности** - каждый модуль отвечает за свою область
2. **Инверсия зависимостей** - сервисы зависят от абстракций
3. **Единая точка входа** - все команды через диспетчер
4. **Асинхронность** - все операции с БД и API асинхронные
5. **Типизация** - использование Pydantic для валидации

### Слои приложения

```
Telegram API → Handlers → Services → Repositories → SQLite Database
     ↑           ↓           ↓
     └── Notifications ← External APIs
```

#### Handlers (Обработчики)
- Обработка команд и callback'ов
- Валидация входных данных
- Вызов сервисов

#### Services (Сервисы)
- Бизнес-логика
- Координация между компонентами
- Интеграция с внешними API

#### Repositories (Репозитории)
- Работа с базой данных
- CRUD операции
- Инкапсуляция SQL

#### Models (Модели)
- Структура данных
- Валидация
- Сериализация

## 🛠️ Команды разработки

### Основные команды

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

### Детальные команды

#### Тестирование
```bash
# Запуск всех тестов
pytest tests/ -v

# Запуск с покрытием
pytest tests/ --cov=src --cov-report=html

# Запуск конкретного теста
pytest tests/test_checkin.py -v

# Запуск тестов с маркерами
pytest tests/ -m "not slow" -v

# Запуск в параллельном режиме
pytest tests/ -n auto
```

#### Форматирование и линтинг
```bash
# Форматирование кода (Black)
black src/ tests/

# Проверка стиля (Flake8)
flake8 src/ tests/

# Проверка типов (MyPy)
mypy src/

# Автоматическое исправление (autopep8)
autopep8 --in-place --recursive src/ tests/
```

#### База данных
```bash
# Создание миграции
alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1

# Просмотр истории миграций
alembic history

# Применение конкретной миграции
alembic upgrade <revision_id>
```

## 🧪 Тестирование

### Стратегия тестирования

- **Unit тесты** (70%) - тестирование отдельных компонентов
- **Integration тесты** (20%) - тестирование взаимодействия
- **E2E тесты** (10%) - тестирование полных сценариев

### Настройка тестирования

```bash
# Установка тестовых зависимостей
pip install pytest pytest-asyncio pytest-cov pytest-mock

# Запуск тестов
pytest tests/ -v

# Запуск с покрытием
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

### Примеры тестов

#### Unit тест сервиса
```python
@pytest.mark.asyncio
async def test_create_checkin_type_1(checkin_service, test_user, test_spot):
    """Тестирование создания чек-ина типа 1 (на месте)."""
    success = await checkin_service.create_checkin(
        test_user, spot_id=1, checkin_type=1, duration=3600
    )
    
    assert success
    checkins = await checkin_service.checkin_repo.get_by_user(123)
    assert len(checkins) == 1
    assert checkins[0].type == 1
    assert checkins[0].active
```

#### Integration тест
```python
@pytest.mark.asyncio
async def test_checkin_flow_integration(
    checkin_handler, spot_service, checkin_service, user_repo
):
    """Тестирование полного потока создания чек-ина."""
    # Подготовка данных
    user = User(id=123, name="Test User")
    spot = Spot(id=1, name="Test Spot", latitude=55.7558, longitude=37.6173)
    
    # Создание пользователя и спота
    await user_repo.create(user.id, user.name)
    await spot_service.add_spot(spot.name, spot.latitude, spot.longitude, "", user.id)
    
    # Создание чек-ина
    success = await checkin_service.create_checkin(user, spot.id, 1, 3600)
    
    # Проверка результата
    assert success
    checkins = await checkin_service.checkin_repo.get_by_user(user.id)
    assert len(checkins) == 1
```

### Фикстуры

```python
@pytest.fixture
async def db():
    """Создает временную in-memory базу данных."""
    async with aiosqlite.connect(":memory:") as db:
        await create_tables(db)
        yield db

@pytest.fixture
async def checkin_service(bot, checkin_repo, notification_service, spot_service, user_repo, weather_service):
    """Фикстура для CheckinService."""
    return CheckinService(bot, checkin_repo, notification_service, spot_service, user_repo, weather_service)
```

## 🗄️ База данных

### Структура таблиц

#### users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    username TEXT,
    timezone TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### spots
```sql
CREATE TABLE spots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    description TEXT,
    created_by INTEGER NOT NULL
);
```

#### checkins
```sql
CREATE TABLE checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    spot_id INTEGER NOT NULL,
    type INTEGER NOT NULL,  -- 1: на месте, 2: прибуду, 3: планирую
    duration INTEGER,       -- в секундах
    created_at DATETIME NOT NULL,
    active_until DATETIME,
    planned_at DATETIME,
    active BOOLEAN DEFAULT TRUE,
    planned_date DATE,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (spot_id) REFERENCES spots (id)
);
```

### Миграции

```bash
# Создание миграции
alembic revision --autogenerate -m "Добавление поля active в checkins"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1

# Просмотр текущей версии
alembic current
```

### Работа с БД в коде

```python
# Создание записи
async def create_user(user_id: int, name: str):
    async with self.db.execute(
        "INSERT INTO users (id, name) VALUES (?, ?)",
        (user_id, name)
    ):
        await self.db.commit()

# Получение записи
async def get_user(user_id: int):
    async with self.db.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return User.from_row(row) if row else None
```

## 🚀 Разработка новых функций

### 1. Создание модели

```python
# src/models/new_feature.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NewFeature(BaseModel):
    """Модель новой функции."""
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    active: bool = True
```

### 2. Создание репозитория

```python
# src/repositories/new_feature.py
import aiosqlite
from typing import List, Optional
from src.models.new_feature import NewFeature

class NewFeatureRepository:
    """Репозиторий для работы с новой функцией."""
    
    def __init__(self, db: aiosqlite.Connection):
        self.db = db
    
    async def create(self, feature: NewFeature) -> int:
        """Создание записи."""
        async with self.db.execute(
            "INSERT INTO new_features (name, description, created_at, active) VALUES (?, ?, ?, ?)",
            (feature.name, feature.description, feature.created_at.isoformat(), int(feature.active))
        ) as cursor:
            await self.db.commit()
            return cursor.lastrowid
    
    async def get_by_id(self, feature_id: int) -> Optional[NewFeature]:
        """Получение записи по ID."""
        async with self.db.execute(
            "SELECT * FROM new_features WHERE id = ?",
            (feature_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return NewFeature.from_row(row) if row else None
```

### 3. Создание сервиса

```python
# src/services/new_feature.py
from src.repositories.new_feature import NewFeatureRepository
from src.models.new_feature import NewFeature
import logging

logger = logging.getLogger(__name__)

class NewFeatureService:
    """Сервис для работы с новой функцией."""
    
    def __init__(self, repo: NewFeatureRepository):
        self.repo = repo
    
    async def create_feature(self, name: str, description: str = None) -> bool:
        """Создание новой функции."""
        try:
            feature = NewFeature(
                id=0,  # Будет установлен в репозитории
                name=name,
                description=description,
                created_at=datetime.utcnow(),
                active=True
            )
            feature_id = await self.repo.create(feature)
            logger.info(f"Создана новая функция с ID {feature_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при создании функции: {e}")
            return False
```

### 4. Создание обработчика

```python
# src/handlers/new_feature.py
from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from src.services.new_feature import NewFeatureService
import logging

logger = logging.getLogger(__name__)

def register_new_feature_handlers(dp: Dispatcher, service: NewFeatureService):
    """Регистрация обработчиков для новой функции."""
    
    @dp.message(Command(commands=["new_feature"]))
    async def cmd_new_feature(message: Message):
        """Обработка команды /new_feature."""
        user_id = message.from_user.id
        logger.info(f"Команда /new_feature от пользователя {user_id}")
        
        try:
            # Извлечение параметров из сообщения
            parts = message.text.split(maxsplit=1)
            if len(parts) < 2:
                await message.answer("Использование: /new_feature <название>")
                return
            
            name = parts[1]
            success = await service.create_feature(name)
            
            if success:
                await message.answer(f"Функция '{name}' успешно создана!")
            else:
                await message.answer("Ошибка при создании функции")
                
        except Exception as e:
            logger.error(f"Ошибка в cmd_new_feature: {e}")
            await message.answer("Произошла ошибка при создании функции")
```

### 5. Интеграция в основной бот

```python
# src/bot.py
from src.handlers.new_feature import register_new_feature_handlers
from src.services.new_feature import NewFeatureService
from src.repositories.new_feature import NewFeatureRepository

# В функции main()
new_feature_repo = NewFeatureRepository(db)
new_feature_service = NewFeatureService(new_feature_repo)
register_new_feature_handlers(dp, new_feature_service)
```

### 6. Создание тестов

```python
# tests/test_new_feature.py
import pytest
from src.services.new_feature import NewFeatureService
from src.repositories.new_feature import NewFeatureRepository

@pytest.mark.asyncio
async def test_create_feature(new_feature_service):
    """Тестирование создания функции."""
    success = await new_feature_service.create_feature("Test Feature", "Test Description")
    assert success

@pytest.mark.asyncio
async def test_get_feature(new_feature_repo):
    """Тестирование получения функции."""
    # Создание тестовой функции
    feature = NewFeature(id=0, name="Test", created_at=datetime.utcnow())
    feature_id = await new_feature_repo.create(feature)
    
    # Получение функции
    retrieved = await new_feature_repo.get_by_id(feature_id)
    assert retrieved is not None
    assert retrieved.name == "Test"
```

### 7. Создание миграции

```bash
# Создание миграции для новой таблицы
alembic revision --autogenerate -m "Добавление таблицы new_features"

# Применение миграции
alembic upgrade head
```

## 🐛 Отладка и логирование

### Логирование

```python
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

# Различные уровни логирования
logger.debug("Отладочная информация")
logger.info("Информационное сообщение")
logger.warning("Предупреждение")
logger.error("Ошибка")
logger.critical("Критическая ошибка")

# Логирование с контекстом
logger.info(f"Создание чек-ина для пользователя {user_id} на споте {spot_id}")

# Логирование исключений
try:
    # код
    pass
except Exception as e:
    logger.error(f"Ошибка при создании чек-ина: {e}", exc_info=True)
```

### Настройка логирования

```python
# В src/bot.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log")
    ]
)
```

### Отладка в Cursor/VS Code

1. **Установка breakpoints** - кликните на номер строки
2. **Запуск в режиме отладки** - F5
3. **Просмотр переменных** - в панели Variables
4. **Выполнение по шагам** - F10 (step over), F11 (step into)

### Отладка асинхронного кода

```python
import asyncio

async def debug_async_function():
    """Отладка асинхронной функции."""
    print("Начало функции")
    
    # Установка breakpoint здесь
    result = await some_async_operation()
    
    print(f"Результат: {result}")
    return result

# Запуск в режиме отладки
if __name__ == "__main__":
    asyncio.run(debug_async_function())
```

## 🚀 Деплой

### Docker

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание пользователя
RUN useradd --create-home --shell /bin/bash app
USER app

# Запуск приложения
CMD ["python", "-m", "src.bot"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  windspotbot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - CHAT_ID=${CHAT_ID}
      - ADMINS=${ADMINS}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=windspotbot
      - POSTGRES_USER=windspotbot
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

#### Запуск
```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f windspotbot

# Остановка
docker-compose down
```

### Системный сервис (systemd)

#### windspotbot.service
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

#### Установка
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

### Переменные окружения для продакшена

```bash
# .env.production
BOT_TOKEN=your_production_bot_token
CHAT_ID=your_production_chat_id
ADMINS=123456789,987654321

# Настройки для продакшена
NEARBY_SPOTS_LIMIT=10
PLANNED_VISITS_LIMIT=10
MIN_SPOT_DISTANCE_M=500

# Интервалы для продакшена
CHECKIN_CHECK_INTERVAL_MINUTES=2
WEATHER_CHECK_INTERVAL_MINUTES=10

# Настройки сообщений
MESSAGE_TTL_DAYS=30
STATS_CACHE_TTL_SECONDS=300

# Настройки подписок
MAX_SUBSCRIPTIONS_PER_USER=20
NOTIFICATION_INTERVAL_SECONDS=30
```

## 📝 Лучшие практики

### 1. Код

#### Именование
```python
# Хорошо
async def create_checkin(user: User, spot_id: int) -> bool:
    """Создание чек-ина для пользователя на споте."""
    pass

# Плохо
async def create(user, id):
    pass
```

#### Документация
```python
async def get_nearby_spots(
    self, 
    lat: float, 
    lon: float, 
    limit: int = 10
) -> List[SpotWithDistance]:
    """
    Получение ближайших спотов к указанным координатам.
    
    Args:
        lat: Широта
        lon: Долгота
        limit: Максимальное количество спотов
        
    Returns:
        Список спотов с расстояниями
        
    Raises:
        ValueError: Если координаты неверные
    """
    pass
```

#### Обработка ошибок
```python
async def safe_operation():
    """Безопасная операция с обработкой ошибок."""
    try:
        result = await risky_operation()
        return result
    except SpecificException as e:
        logger.error(f"Специфическая ошибка: {e}")
        return None
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
        raise
```

### 2. Тестирование

#### Покрытие кода
```bash
# Целевое покрытие: >80%
pytest tests/ --cov=src --cov-report=html --cov-fail-under=80
```

#### Именование тестов
```python
def test_create_checkin_type_1_on_spot():
    """Тест создания чек-ина типа 1 на споте."""
    pass

def test_create_checkin_with_invalid_spot_raises_error():
    """Тест создания чек-ина с несуществующим спотом вызывает ошибку."""
    pass
```

### 3. Git

#### Коммиты
```bash
# Хорошие сообщения коммитов
git commit -m "feat: добавлена поддержка планирования поездок"
git commit -m "fix: исправлена ошибка в расчете расстояний"
git commit -m "docs: обновлена документация API"

# Плохие сообщения
git commit -m "fix"
git commit -m "update"
git commit -m "changes"
```

#### Ветки
```bash
# Создание ветки для новой функции
git checkout -b feature/planned-checkins

# Создание ветки для исправления
git checkout -b fix/distance-calculation

# Создание ветки для документации
git checkout -b docs/api-update
```

### 4. Производительность

#### Асинхронность
```python
# Хорошо - параллельное выполнение
async def get_spot_data(spot_id: int):
    weather_task = asyncio.create_task(get_weather(spot_id))
    users_task = asyncio.create_task(get_active_users(spot_id))
    
    weather, users = await asyncio.gather(weather_task, users_task)
    return weather, users

# Плохо - последовательное выполнение
async def get_spot_data(spot_id: int):
    weather = await get_weather(spot_id)
    users = await get_active_users(spot_id)
    return weather, users
```

#### Кэширование
```python
from functools import lru_cache
import asyncio

@lru_cache(maxsize=128)
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Кэшированный расчет расстояния."""
    # Расчет расстояния
    pass
```

## 🔧 Troubleshooting

### Частые проблемы

#### 1. Ошибка импорта модулей
```bash
# Проблема
ModuleNotFoundError: No module named 'src'

# Решение
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Или
python -m src.bot
```

#### 2. Ошибка подключения к базе данных
```bash
# Проблема
sqlite3.OperationalError: database is locked

# Решение
# Проверьте, что база данных не используется другим процессом
# Убедитесь, что все соединения закрыты
```

#### 3. Ошибка аутентификации бота
```bash
# Проблема
aiogram.exceptions.TelegramUnauthorizedError: Unauthorized

# Решение
# Проверьте BOT_TOKEN в .env
# Убедитесь, что токен действителен
```

#### 4. Ошибка миграций
```bash
# Проблема
alembic.util.exc.CommandError: Can't locate revision identified by 'head'

# Решение
# Сброс миграций
alembic stamp head
# Или создание новой миграции
alembic revision --autogenerate -m "Initial migration"
```

### Отладка производительности

#### Профилирование
```python
import cProfile
import pstats

def profile_function():
    """Профилирование функции."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Ваш код здесь
    result = some_function()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return result
```

#### Мониторинг памяти
```python
import tracemalloc

def monitor_memory():
    """Мониторинг использования памяти."""
    tracemalloc.start()
    
    # Ваш код здесь
    result = some_function()
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")
    
    tracemalloc.stop()
    return result
```

### Логи и мониторинг

#### Настройка логирования
```python
import logging
import logging.handlers

def setup_logging():
    """Настройка системы логирования."""
    # Создание логгера
    logger = logging.getLogger('windspotbot')
    logger.setLevel(logging.INFO)
    
    # Обработчик для файла
    file_handler = logging.handlers.RotatingFileHandler(
        'bot.log', maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Форматирование
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Добавление обработчиков
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

## 📚 Дополнительные ресурсы

### Документация
- [aiogram 3.x](https://docs.aiogram.dev/)
- [SQLAlchemy 2.x](https://docs.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [pytest](https://docs.pytest.org/)

### Полезные инструменты
- [Postman](https://www.postman.com/) - тестирование API
- [DBeaver](https://dbeaver.io/) - работа с БД
- [Redis Desktop Manager](https://rdm.dev/) - работа с Redis
- [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Сообщество
- [Telegram канал проекта](https://t.me/WindSpotRU)
- [Чат для разработчиков](https://t.me/WindSpotChat)
- [GitHub Issues](https://github.com/your-repo/issues)

---

Это руководство поможет вам эффективно разрабатывать и поддерживать WindSpotBot! 🚀

Если у вас есть вопросы или предложения по улучшению документации, создайте issue в репозитории.
