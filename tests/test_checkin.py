import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
import aiosqlite
from src.services.checkin import CheckinService
from src.repositories.checkin import CheckinRepository
from src.repositories.user import UserRepository
from src.repositories.spot import SpotRepository
from src.services.geo import GeoService
from src.services.notification import NotificationService
from src.services.weather import WeatherService
from src.services.spot import SpotService
from src.services.scheduler import SchedulerService
from src.models.checkin import Checkin
from src.models.user import User
from src.models.spot import Spot

# Фикстуры для тестов
@pytest.fixture
async def db():
    """Создает временную in-memory базу данных."""
    async with aiosqlite.connect(":memory:") as db:
        await db.execute("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                username TEXT,
                timezone TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE spots (
                id INTEGER PRIMARY KEY,
                name TEXT,
                latitude REAL,
                longitude REAL
            )
        """)
        await db.execute("""
            CREATE TABLE checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                spot_id INTEGER,
                type INTEGER,
                duration INTEGER,
                created_at TEXT,
                active_until TEXT,
                planned_at TEXT,
                active INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (spot_id) REFERENCES spots (id)
            )
        """)
        await db.commit()
        yield db

@pytest.fixture
def bot():
    """Мок для aiogram Bot."""
    bot = MagicMock()
    bot.send_message = AsyncMock()
    return bot

@pytest.fixture
def geo_service():
    """Мок для GeoService."""
    geo_service = MagicMock(spec=GeoService)
    geo_service.get_cached_location = AsyncMock(return_value=(55.7558, 37.6173))
    geo_service.get_timezone = AsyncMock(return_value="Europe/Moscow")
    return geo_service

@pytest.fixture
def notification_service():
    """Мок для NotificationService."""
    notification_service = MagicMock(spec=NotificationService)
    notification_service.send_checkin_notification = AsyncMock()
    notification_service.send_checkout_notification = AsyncMock()
    notification_service.send_spot_checkin_notification = AsyncMock()
    notification_service.send_spot_checkout_notification = AsyncMock()
    return notification_service

@pytest.fixture
def weather_service():
    """Мок для WeatherService."""
    weather_service = MagicMock(spec=WeatherService)
    weather_service.get_weather = AsyncMock(return_value={"wind_speed": 5.0})
    return weather_service

@pytest.fixture
async def user_repo(db):
    """Фикстура для UserRepository."""
    return UserRepository(db)

@pytest.fixture
async def spot_repo(db):
    """Фикстура для SpotRepository."""
    return SpotRepository(db)

@pytest.fixture
async def checkin_repo(db):
    """Фикстура для CheckinRepository."""
    return CheckinRepository(db)

@pytest.fixture
async def spot_service(spot_repo, geo_service):
    """Фикстура для SpotService."""
    return SpotService(spot_repo, geo_service)

@pytest.fixture
async def checkin_service(bot, checkin_repo, notification_service, spot_service, user_repo, weather_service):
    """Фикстура для CheckinService."""
    return CheckinService(bot, checkin_repo, notification_service, spot_service, user_repo, weather_service)

@pytest.fixture
def scheduler_service(checkin_service):
    """Фикстура для SchedulerService."""
    scheduler = MagicMock()
    scheduler_service = SchedulerService(scheduler, checkin_service)
    return scheduler_service

@pytest.fixture
async def test_user(user_repo):
    """Создает тестового пользователя."""
    user = User(user_id=123, name="Test User", username="testuser", timezone="Europe/Moscow")
    await user_repo.create(user_id=user.user_id, name=user.name, username=user.username, timezone=user.timezone)
    return user

@pytest.fixture
async def test_spot(spot_repo):
    """Создает тестовый спот."""
    spot = Spot(id=1, name="Test Spot", latitude=55.7558, longitude=37.6173)
    await spot_repo.create(spot.name, spot.latitude, spot.longitude)
    return spot

@pytest.fixture
async def test_spot_2(spot_repo):
    """Создает второй тестовый спот."""
    spot = Spot(id=2, name="Test Spot 2", latitude=55.7658, longitude=37.6273)
    await spot_repo.create(spot.name, spot.latitude, spot.longitude)
    return spot

# Тесты
@pytest.mark.asyncio
async def test_create_checkin_type_1(checkin_service, test_user, test_spot):
    """Тестирование создания чек-ина типа 1 (на месте)."""
    user_id = 123
    spot_id = 1
    duration = 3600  # 1 час
    success = await checkin_service.create_checkin(test_user, spot_id, checkin_type=1, duration=duration)
    
    assert success
    checkins = await checkin_service.checkin_repo.get_by_user(user_id)
    assert len(checkins) == 1
    checkin = checkins[0]
    assert checkin.user_id == user_id
    assert checkin.spot_id == spot_id
    assert checkin.type == 1
    assert checkin.duration == duration
    assert checkin.active
    assert checkin_service.notification_service.send_checkin_notification.called

@pytest.mark.asyncio
async def test_manual_leave_spot_type_1_not_expired(checkin_service, test_user, test_spot):
    """Тестирование ручного разчек-ина типа 1 (по кнопке, не просрочен)."""
    user_id = 123
    spot_id = 1
    duration = 3600
    success = await checkin_service.create_checkin(test_user, spot_id, checkin_type=1, duration=duration)
    assert success
    checkins = await checkin_service.checkin_repo.get_by_user(user_id)
    checkin = checkins[0]
    
    await checkin_service.deactivate_checkin(checkin.id, update_duration=True)
    
    updated_checkin = await checkin_service.checkin_repo.get_by_id(checkin.id)
    assert updated_checkin.active == False
    assert updated_checkin.active_until > checkin.active_until  # Обновлено на текущее время
    expected_duration = int((updated_checkin.active_until - updated_checkin.created_at).total_seconds())
    assert updated_checkin.duration == expected_duration
    assert checkin_service.notification_service.send_checkout_notification.called

@pytest.mark.asyncio
async def test_manual_leave_spot_type_1_expired(checkin_service, test_user, test_spot):
    """Тестирование ручного разчек-ина типа 1 (по кнопке, просрочен)."""
    user_id = 123
    spot_id = 1
    duration = 3600
    created_at = datetime.utcnow() - timedelta(minutes=70)  # Чек-ин создан 70 минут назад
    active_until = created_at + timedelta(minutes=60)  # Истек 10 минут назад
    checkin = Checkin(
        id=0,
        user_id=user_id,
        spot_id=spot_id,
        type=1,
        duration=duration,
        created_at=created_at,
        active_until=active_until,
        planned_at=None,
        active=True
    )
    checkin_id = await checkin_service.checkin_repo.create(checkin)
    
    await checkin_service.deactivate_checkin(checkin_id, update_duration=False)
    
    updated_checkin = await checkin_service.checkin_repo.get_by_id(checkin_id)
    assert updated_checkin.active == False
    assert updated_checkin.active_until == active_until  # Не изменилось
    assert updated_checkin.duration == duration  # Не изменилось
    assert checkin_service.notification_service.send_checkout_notification.called

@pytest.mark.asyncio
async def test_checkin_new_spot_deactivates_previous_type_1(checkin_service, test_user, test_spot, test_spot_2):
    """Тестирование разчек-ина при новом чек-ине на другом споте."""
    user_id = 123
    spot_id_1 = 1
    spot_id_2 = 2
    duration = 3600
    
    # Первый чек-ин
    success = await checkin_service.create_checkin(test_user, spot_id_1, checkin_type=1, duration=duration)
    assert success
    checkins = await checkin_service.checkin_repo.get_by_user(user_id)
    first_checkin = checkins[0]
    
    # Новый чек-ин на другом споте
    success = await checkin_service.create_checkin(test_user, spot_id_2, checkin_type=1, duration=duration)
    assert success
    
    # Проверка первого чек-ина
    updated_first_checkin = await checkin_service.checkin_repo.get_by_id(first_checkin.id)
    assert updated_first_checkin.active == False
    assert updated_first_checkin.active_until > first_checkin.active_until
    expected_duration = int((updated_first_checkin.active_until - updated_first_checkin.created_at).total_seconds())
    assert updated_first_checkin.duration == expected_duration
    
    # Проверка второго чек-ина
    checkins = await checkin_service.checkin_repo.get_by_user(user_id)
    second_checkin = checkins[0]
    assert second_checkin.spot_id == spot_id_2
    assert checkin_service.notification_service.send_checkout_notification.called

@pytest.mark.asyncio
async def test_auto_leave_expired_checkins_type_1(scheduler_service, checkin_service, test_user, test_spot):
    """Тестирование автоматического разчек-ина типа 1."""
    user_id = 123
    spot_id = 1
    duration = 3600
    created_at = datetime.utcnow() - timedelta(minutes=70)
    active_until = created_at + timedelta(minutes=60)
    checkin = Checkin(
        id=0,
        user_id=user_id,
        spot_id=spot_id,
        type=1,
        duration=duration,
        created_at=created_at,
        active_until=active_until,
        planned_at=None,
        active=True
    )
    checkin_id = await checkin_service.checkin_repo.create(checkin)
    
    await scheduler_service.check_expired_checkins()
    
    updated_checkin = await checkin_service.checkin_repo.get_by_id(checkin_id)
    assert updated_checkin.active == False
    assert updated_checkin.active_until == active_until  # Не изменилось
    assert updated_checkin.duration == duration  # Не изменилось
    assert checkin_service.notification_service.send_checkout_notification.called

@pytest.mark.asyncio
async def test_extend_checkin_type_1(checkin_service, test_user, test_spot):
    """Тестирование продления чек-ина типа 1."""
    user_id = 123
    spot_id = 1
    duration = 3600
    success = await checkin_service.create_checkin(test_user, spot_id, checkin_type=1, duration=duration)
    assert success
    checkins = await checkin_service.checkin_repo.get_by_user(user_id)
    checkin = checkins[0]
    
    new_active_until = checkin.active_until + timedelta(hours=1)
    new_duration = checkin.duration + 3600
    success = await checkin_service.update_checkin_duration(checkin.id, new_active_until, new_duration)
    
    assert success
    updated_checkin = await checkin_service.checkin_repo.get_by_id(checkin.id)
    assert updated_checkin.active == True
    assert updated_checkin.active_until == new_active_until
    assert updated_checkin.duration == new_duration

@pytest.mark.asyncio
async def test_create_checkin_type_2(checkin_service, test_user, test_spot):
    """Тестирование создания чек-ина типа 2 (планирование)."""
    user_id = 123
    spot_id = 1
    duration = 3600
    success = await checkin_service.create_checkin(test_user, spot_id, checkin_type=2, duration=duration)
    
    assert success
    checkins = await checkin_service.checkin_repo.get_by_user(user_id)
    assert len(checkins) == 1
    checkin = checkins[0]
    assert checkin.user_id == user_id
    assert checkin.spot_id == spot_id
    assert checkin.type == 2
    assert checkin.duration == duration
    assert checkin.active
    assert checkin.planned_at is not None
    assert checkin_service.notification_service.send_checkin_notification.called

@pytest.mark.asyncio
async def test_create_checkin_spot_not_found(checkin_service, test_user):
    """Тестирование создания чек-ина с несуществующим спотом."""
    user_id = 123
    spot_id = 999
    success = await checkin_service.create_checkin(test_user, spot_id, checkin_type=1, duration=3600)
    
    assert not success
    checkins = await checkin_service.checkin_repo.get_by_user(user_id)
    assert len(checkins) == 0
    assert checkin_service.bot.send_message.called
