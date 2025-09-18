# Архитектура WindSpotBot 🏗️

WindSpotBot использует модульную архитектуру с четким разделением ответственности между слоями. Это обеспечивает независимость бизнес-логики от обработчиков, удобство тестирования и масштабируемость.

## 🎯 Принципы архитектуры

- **Разделение ответственности** - каждый модуль отвечает за свою область
- **Инверсия зависимостей** - сервисы зависят от абстракций, а не от конкретных реализаций
- **Единая точка входа** - все команды проходят через единый диспетчер
- **Асинхронность** - все операции с БД и внешними API асинхронные
- **Типизация** - использование Pydantic для валидации данных

## 📁 Структура проекта

### Handlers (Обработчики команд)
```
src/handlers/
├── start.py       # Команда /start, регистрация пользователей
├── checkin.py     # Чек-ины на спотах (3 типа)
├── activity.py    # Активность на спотах, погода, пользователи
├── main_menu.py   # Главное меню, навигация
└── plans.py       # Планирование поездок
```

**Ответственность**: Обработка команд и callback'ов от пользователей, валидация входных данных, вызов сервисов.

### Services (Бизнес-логика)
```
src/services/
├── checkin.py        # Управление чек-инами
├── spot.py          # Управление спотами
├── geo.py           # Работа с геолокацией
├── weather.py       # Данные о погоде
├── notification.py  # Уведомления
├── chat.py          # Чаты спотов
├── topic.py         # Темы в Telegram
├── scheduler.py     # Планировщик задач
├── stats.py         # Статистика
└── rating.py        # Оценка спотов
```

**Ответственность**: Реализация бизнес-логики, координация между репозиториями и внешними API.

### Repositories (Работа с БД)
```
src/repositories/
├── user.py         # Пользователи
├── spot.py         # Споты
├── checkin.py      # Чек-ины
└── subscription.py # Подписки
```

**Ответственность**: Инкапсуляция работы с базой данных, CRUD операции.

### Models (Модели данных)
```
src/models/
├── user.py         # User, UserProfile
├── spot.py         # Spot, SpotWithDistance
├── checkin.py      # Checkin
└── subscription.py # Subscription
```

**Ответственность**: Определение структуры данных, валидация, сериализация.

## 🔄 Схема взаимодействия

```
Telegram API → Handlers → Services → Repositories → SQLite Database
     ↑           ↓           ↓
     └── Notifications ← External APIs
```

### Поток данных

1. **Входящее сообщение** → Handler
2. **Handler** → Service (бизнес-логика)
3. **Service** → Repository (данные)
4. **Service** → External API (погода, геолокация)
5. **Service** → NotificationService (уведомления)
6. **Response** ← Handler ← Service

## 🏢 Детальное описание компонентов

### Handlers Layer

#### StartHandler (`src/handlers/start.py`)
- **Функции**: Регистрация новых пользователей, приветствие
- **Состояния**: `requesting_location`
- **Зависимости**: `UserRepository`, `CheckinRepository`

#### CheckinHandler (`src/handlers/checkin.py`)
- **Функции**: Создание чек-инов, выбор спотов, типов чек-инов
- **Состояния**: `requesting_location`, `selecting_spot`, `selecting_type`, `selecting_duration`
- **Зависимости**: `GeoService`, `SpotService`, `CheckinService`

#### ActivityHandler (`src/handlers/activity.py`)
- **Функции**: Показ активности на спотах, погоды, пользователей
- **Состояния**: `requesting_location`
- **Зависимости**: `SpotService`, `CheckinService`, `WeatherService`, `ChatService`

### Services Layer

#### CheckinService (`src/services/checkin.py`)
```python
class CheckinService:
    async def create_checkin(self, user: User, spot_id: int, checkin_type: int, duration: int) -> bool
    async def get_active_users(self, spot_id: int) -> Tuple[List[User], List[User]]
    async def deactivate_checkin(self, checkin_id: int, update_duration: bool = True) -> bool
    async def extend_checkin(self, checkin_id: int, hours: int) -> bool
```

**Типы чек-инов**:
- **Тип 1**: На месте (с длительностью)
- **Тип 2**: Прибуду (с планируемым временем)
- **Тип 3**: Планирую (с датой)

#### SpotService (`src/services/spot.py`)
```python
class SpotService:
    async def get_nearby_spots(self, lat: float, lon: float, limit: int) -> List[SpotWithDistance]
    async def add_spot(self, name: str, lat: float, lon: float, description: str, user_id: int) -> int
    async def get_spot_by_id(self, spot_id: int) -> Optional[Spot]
    async def get_all_spots(self) -> List[Spot]
```

#### GeoService (`src/services/geo.py`)
```python
class GeoService:
    async def get_nearby_spots(self, spots: List[Spot], lat: float, lon: float) -> List[SpotWithDistance]
    async def get_cached_location(self, user_id: int) -> Optional[Tuple[float, float]]
    async def cache_location(self, user_id: int, lat: float, lon: float) -> None
    async def get_timezone(self, lat: float, lon: float) -> str
```

#### WeatherService (`src/services/weather.py`)
```python
class WeatherService:
    async def get_weather(self, lat: float, lon: float) -> Dict[str, Any]
    async def get_water_temperature(self, lat: float, lon: float) -> Optional[float]
    async def get_wind_speed(self, lat: float, lon: float) -> Optional[float]
```

#### NotificationService (`src/services/notification.py`)
```python
class NotificationService:
    async def send_checkin_notification(self, user: User, spot_name: str) -> None
    async def send_checkout_notification(self, user: User, spot_name: str) -> None
    async def send_weather_notification(self, spot_name: str, weather_data: Dict) -> None
    async def send_message_notification(self, spot_name: str, message: str, author: User) -> None
```

#### SchedulerService (`src/services/scheduler.py`)
```python
class SchedulerService:
    def add_checkin_expiration_job(self, interval_minutes: int) -> None
    def add_checkin_warning_job(self, interval_minutes: int) -> None
    def add_planned_checkin_reminder_job(self) -> None
    async def check_expired_checkins(self) -> None
```

### Repositories Layer

#### UserRepository (`src/repositories/user.py`)
```python
class UserRepository:
    async def create(self, user_id: int, name: str, username: Optional[str] = None) -> int
    async def get_by_id(self, user_id: int) -> Optional[User]
    async def update_timezone(self, user_id: int, timezone: str) -> None
```

#### SpotRepository (`src/repositories/spot.py`)
```python
class SpotRepository:
    async def create(self, spot: Spot) -> int
    async def get_by_id(self, spot_id: int) -> Optional[Spot]
    async def get_by_name(self, name: str) -> Optional[Spot]
    async def get_all(self) -> List[Spot]
```

#### CheckinRepository (`src/repositories/checkin.py`)
```python
class CheckinRepository:
    async def create(self, checkin: Checkin) -> int
    async def get_by_user(self, user_id: int) -> List[Checkin]
    async def get_by_spot(self, spot_id: int) -> List[Checkin]
    async def get_active_checkins(self) -> List[Checkin]
    async def update(self, checkin_id: int, **kwargs) -> bool
    async def deactivate(self, checkin_id: int) -> bool
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

#### subscriptions
```sql
CREATE TABLE subscriptions (
    user_id INTEGER NOT NULL,
    spot_name TEXT NOT NULL,
    event_type TEXT NOT NULL,  -- checkin, message, weather
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, spot_name, event_type)
);
```

#### spot_topics
```sql
CREATE TABLE spot_topics (
    spot_name TEXT PRIMARY KEY,
    thread_id INTEGER NOT NULL
);
```

### Миграции

Проект использует Alembic для управления миграциями:

```bash
# Создание миграции
alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

## 🔧 Конфигурация

### Основные настройки (`src/config/config.py`)

```python
class Settings(BaseSettings):
    BOT_TOKEN: str
    CHAT_ID: int
    ADMINS: List[int]
    NEARBY_SPOTS_LIMIT: int = 5
    PLANNED_VISITS_LIMIT: int = 5
    CHECKIN_CHECK_INTERVAL_MINUTES: int = 5
    WEATHER_CHECK_INTERVAL_MINUTES: int = 15
    MESSAGE_TTL_DAYS: int = 7
    STATS_CACHE_TTL_SECONDS: int = 600
    MAX_SUBSCRIPTIONS_PER_USER: int = 10
    NOTIFICATION_INTERVAL_SECONDS: int = 60
    MIN_SPOT_DISTANCE_M: int = 300
```

### Настройки тем (`src/config/topics.py`)

```python
class TopicConfig:
    SPOT_TOPICS: Dict[str, int] = {
        "Должанка": 0,
        "Ейск": 0,
        "Анапа": 0,
    }
```

## 🔄 Потоки данных

### Создание чек-ина

1. **Пользователь** → `/checkin` → `CheckinHandler`
2. **CheckinHandler** → запрос геолокации → `GeoService`
3. **GeoService** → кэширование координат
4. **CheckinHandler** → получение ближайших спотов → `SpotService`
5. **SpotService** → `GeoService.get_nearby_spots()`
6. **Пользователь** → выбор спота и типа → `CheckinHandler`
7. **CheckinHandler** → создание чек-ина → `CheckinService`
8. **CheckinService** → сохранение в БД → `CheckinRepository`
9. **CheckinService** → отправка уведомлений → `NotificationService`

### Показ активности

1. **Пользователь** → `/activity` → `ActivityHandler`
2. **ActivityHandler** → получение геолокации → `GeoService`
3. **ActivityHandler** → получение спотов → `SpotService`
4. **ActivityHandler** → получение активных пользователей → `CheckinService`
5. **ActivityHandler** → получение погоды → `WeatherService`
6. **ActivityHandler** → получение ссылок на чаты → `ChatService`
7. **ActivityHandler** → формирование ответа → **Пользователь**

## 🚀 Планировщик задач

### Регулярные задачи

- **Проверка истечения чек-инов** (каждые 5 минут)
- **Предупреждения о скором истечении** (каждые 2 минуты)
- **Уведомления о запланированных чек-инах** (каждые 2 минуты)
- **Удаление просроченных чек-инов типа 2** (каждые 5 минут)
- **Напоминания о запланированных поездках** (ежедневно)
- **Удаление просроченных чек-инов типа 3** (ежедневно)

### Настройка планировщика

```python
scheduler_service = SchedulerService(scheduler, checkin_service)
scheduler_service.start()
scheduler_service.add_checkin_expiration_job(interval_minutes=5)
scheduler_service.add_checkin_warning_job(interval_minutes=2)
```

## 🔔 Система уведомлений

### Типы уведомлений

1. **Чек-ины**: Уведомления о новых чек-инах на спотах
2. **Сообщения**: Уведомления о новых сообщениях в чатах спотов
3. **Погода**: Уведомления об изменении погодных условий

### Подписки

Пользователи могут подписываться на события по спотам:
- `checkin` - чек-ины на споте
- `message` - сообщения в чате спота
- `weather` - изменения погоды на споте

## 🧪 Тестирование

### Архитектура тестов

- **Unit тесты** - тестирование отдельных сервисов и репозиториев
- **Integration тесты** - тестирование взаимодействия между компонентами
- **E2E тесты** - тестирование полных пользовательских сценариев

### Фикстуры

```python
@pytest.fixture
async def db():
    """Создает временную in-memory базу данных."""
    async with aiosqlite.connect(":memory:") as db:
        # Создание таблиц
        yield db

@pytest.fixture
async def checkin_service(bot, checkin_repo, notification_service, spot_service, user_repo, weather_service):
    """Фикстура для CheckinService."""
    return CheckinService(bot, checkin_repo, notification_service, spot_service, user_repo, weather_service)
```

## 🔒 Безопасность

### Валидация данных

- **Pydantic модели** для валидации входящих данных
- **Проверка прав доступа** для административных команд
- **Санитизация пользовательского ввода**

### Обработка ошибок

- **Централизованная обработка** через `@dp.error()`
- **Логирование всех ошибок** с контекстом
- **Graceful degradation** при недоступности внешних сервисов

## 📈 Масштабируемость

### Горизонтальное масштабирование

- **Stateless сервисы** - можно запускать несколько экземпляров
- **Внешняя база данных** - PostgreSQL для продакшена
- **Кэширование** - Redis для кэширования часто используемых данных

### Вертикальное масштабирование

- **Асинхронная архитектура** - эффективное использование ресурсов
- **Connection pooling** для базы данных
- **Batch операции** для массовых уведомлений

## 🔧 Мониторинг и логирование

### Логирование

```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"Создание чек-ина для пользователя {user_id}")
logger.error(f"Ошибка при создании чек-ина: {e}")
```

### Метрики

- Количество активных пользователей
- Количество чек-инов в день
- Популярность спотов
- Время отклика API

---

Эта архитектура обеспечивает гибкость, тестируемость и возможность легкого расширения функциональности WindSpotBot.



