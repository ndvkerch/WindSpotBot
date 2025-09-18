# Тестирование WindSpotBot 🧪

WindSpotBot использует комплексный подход к тестированию, включающий unit-тесты, интеграционные тесты и end-to-end тестирование. Это обеспечивает стабильность и корректность работы бота.

## 🎯 Стратегия тестирования

### Пирамида тестирования

```
    E2E Tests (мало)
        ↑
  Integration Tests (средне)
        ↑
   Unit Tests (много)
```

- **Unit тесты** (70%) - тестирование отдельных компонентов
- **Integration тесты** (20%) - тестирование взаимодействия компонентов
- **E2E тесты** (10%) - тестирование полных пользовательских сценариев

## 🛠️ Настройка тестирования

### 1. Установка зависимостей

```bash
# Установка тестовых зависимостей
pip install pytest pytest-asyncio pytest-cov pytest-mock

# Или через requirements.txt
pip install -r requirements.txt
```

### 2. Конфигурация pytest

Файл `pytest.ini` уже настроен:
```ini
[pytest]
pythonpath = .
asyncio_default_fixture_loop_scope = function
```

### 3. Структура тестов

```
tests/
├── __init__.py
├── conftest.py          # Общие фикстуры
├── test_bot.py          # Тесты основного бота
├── test_checkin.py      # Тесты чек-инов
├── test_services/       # Тесты сервисов
│   ├── test_checkin_service.py
│   ├── test_spot_service.py
│   ├── test_geo_service.py
│   ├── test_weather_service.py
│   └── test_notification_service.py
├── test_repositories/   # Тесты репозиториев
│   ├── test_user_repository.py
│   ├── test_spot_repository.py
│   └── test_checkin_repository.py
├── test_handlers/       # Тесты обработчиков
│   ├── test_start_handler.py
│   ├── test_checkin_handler.py
│   └── test_activity_handler.py
└── test_integration/    # Интеграционные тесты
    ├── test_checkin_flow.py
    └── test_activity_flow.py
```

## 🚀 Запуск тестов

### Основные команды

```bash
# Запуск всех тестов
pytest tests/ -v

# Запуск с покрытием кода
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Запуск конкретного теста
pytest tests/test_checkin.py -v

# Запуск тестов с маркерами
pytest tests/ -m "not slow" -v

# Запуск в параллельном режиме
pytest tests/ -n auto
```

### Через Makefile

```bash
# Запуск тестов
make test

# Запуск с покрытием
make test-coverage

# Запуск только быстрых тестов
make test-fast
```

## 🧪 Типы тестов

### Unit тесты

Тестирование отдельных компонентов в изоляции.

#### Пример теста сервиса

```python
@pytest.mark.asyncio
async def test_create_checkin_type_1(checkin_service, test_user, test_spot):
    """Тестирование создания чек-ина типа 1 (на месте)."""
    user_id = 123
    spot_id = 1
    duration = 3600  # 1 час
    
    success = await checkin_service.create_checkin(
        test_user, spot_id, checkin_type=1, duration=duration
    )
    
    assert success
    checkins = await checkin_service.checkin_repo.get_by_user(user_id)
    assert len(checkins) == 1
    checkin = checkins[0]
    assert checkin.user_id == user_id
    assert checkin.spot_id == spot_id
    assert checkin.type == 1
    assert checkin.duration == duration
    assert checkin.active
```

#### Пример теста репозитория

```python
@pytest.mark.asyncio
async def test_create_user(user_repo):
    """Тестирование создания пользователя."""
    user_id = 123
    name = "Test User"
    username = "testuser"
    
    result = await user_repo.create(user_id, name, username)
    
    assert result == user_id
    user = await user_repo.get_by_id(user_id)
    assert user is not None
    assert user.id == user_id
    assert user.name == name
    assert user.username == username
```

### Integration тесты

Тестирование взаимодействия между компонентами.

#### Пример интеграционного теста

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

### E2E тесты

Тестирование полных пользовательских сценариев.

#### Пример E2E теста

```python
@pytest.mark.asyncio
async def test_full_checkin_flow():
    """Тестирование полного потока чек-ина от команды до уведомления."""
    # Имитация команды /checkin
    message = create_test_message("/checkin")
    
    # Обработка команды
    await checkin_handler.cmd_checkin(message)
    
    # Проверка ответа
    assert message.answer.called
    response = message.answer.call_args[0][0]
    assert "Выбери спот для чек-ина" in response
```

## 🔧 Фикстуры

### Общие фикстуры (`tests/conftest.py`)

```python
@pytest.fixture
async def db():
    """Создает временную in-memory базу данных."""
    async with aiosqlite.connect(":memory:") as db:
        # Создание таблиц
        await create_tables(db)
        yield db

@pytest.fixture
def bot():
    """Мок для aiogram Bot."""
    bot = MagicMock()
    bot.send_message = AsyncMock()
    return bot

@pytest.fixture
async def checkin_service(bot, checkin_repo, notification_service, spot_service, user_repo, weather_service):
    """Фикстура для CheckinService."""
    return CheckinService(bot, checkin_repo, notification_service, spot_service, user_repo, weather_service)

@pytest.fixture
async def test_user(user_repo):
    """Создает тестового пользователя."""
    user = User(id=123, name="Test User", username="testuser")
    await user_repo.create(user.id, user.name, user.username)
    return user

@pytest.fixture
async def test_spot(spot_repo):
    """Создает тестовый спот."""
    spot = Spot(id=1, name="Test Spot", latitude=55.7558, longitude=37.6173)
    await spot_repo.create(spot)
    return spot
```

### Специализированные фикстуры

```python
@pytest.fixture
def mock_weather_api():
    """Мок для WeatherService."""
    with patch('src.services.weather.WeatherService.get_weather') as mock:
        mock.return_value = {
            "wind_speed": 5.0,
            "temperature": 20.0,
            "water_temperature": 18.0
        }
        yield mock

@pytest.fixture
def mock_geo_service():
    """Мок для GeoService."""
    geo_service = MagicMock(spec=GeoService)
    geo_service.get_cached_location = AsyncMock(return_value=(55.7558, 37.6173))
    geo_service.get_timezone = AsyncMock(return_value="Europe/Moscow")
    return geo_service
```

## 📊 Покрытие кода

### Настройка покрытия

```bash
# Запуск с покрытием
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Покрытие с исключениями
pytest tests/ --cov=src --cov-report=html --cov-omit="*/migrations/*,*/tests/*"
```

### Цели покрытия

- **Общее покрытие**: > 80%
- **Критический код**: > 90%
- **Сервисы**: > 85%
- **Репозитории**: > 90%

### Исключения из покрытия

```python
# В коде можно использовать комментарии для исключения
def some_function():
    if DEBUG:  # pragma: no cover
        print("Debug info")
    
    # Сложная логика, которую сложно протестировать
    try:
        result = complex_operation()
    except Exception:  # pragma: no cover
        # Обработка редких ошибок
        pass
```

## 🏷️ Маркеры тестов

### Определение маркеров

```python
# В conftest.py
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
```

### Использование маркеров

```python
@pytest.mark.slow
@pytest.mark.asyncio
async def test_heavy_operation():
    """Тест, который выполняется долго."""
    # Тяжелая операция
    pass

@pytest.mark.integration
@pytest.mark.asyncio
async def test_service_integration():
    """Интеграционный тест."""
    pass

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_full_user_flow():
    """E2E тест."""
    pass
```

### Запуск по маркерам

```bash
# Только быстрые тесты
pytest tests/ -m "not slow"

# Только интеграционные тесты
pytest tests/ -m "integration"

# Исключить E2E тесты
pytest tests/ -m "not e2e"
```

## 🔍 Тестирование асинхронного кода

### Использование pytest-asyncio

```python
@pytest.mark.asyncio
async def test_async_function():
    """Тест асинхронной функции."""
    result = await some_async_function()
    assert result is not None

@pytest.mark.asyncio
async def test_async_with_fixtures(db, user_repo):
    """Тест с асинхронными фикстурами."""
    user = await user_repo.create(123, "Test User")
    assert user is not None
```

### Тестирование с моками

```python
@pytest.mark.asyncio
async def test_with_mocks():
    """Тест с моками асинхронных функций."""
    with patch('src.services.weather.WeatherService.get_weather') as mock_weather:
        mock_weather.return_value = {"wind_speed": 5.0}
        
        weather_service = WeatherService()
        result = await weather_service.get_weather(55.7558, 37.6173)
        
        assert result["wind_speed"] == 5.0
        mock_weather.assert_called_once_with(55.7558, 37.6173)
```

## 🚨 Тестирование ошибок

### Тестирование исключений

```python
@pytest.mark.asyncio
async def test_database_error():
    """Тест обработки ошибок базы данных."""
    with patch('src.repositories.user.UserRepository.create') as mock_create:
        mock_create.side_effect = Exception("Database error")
        
        user_repo = UserRepository(db)
        
        with pytest.raises(Exception, match="Database error"):
            await user_repo.create(123, "Test User")
```

### Тестирование валидации

```python
def test_invalid_user_data():
    """Тест валидации данных пользователя."""
    with pytest.raises(ValidationError):
        User(id="invalid", name="")  # Неверный тип ID и пустое имя
```

## 📈 Производительность тестов

### Параллельное выполнение

```bash
# Установка pytest-xdist
pip install pytest-xdist

# Запуск в параллельном режиме
pytest tests/ -n auto
```

### Оптимизация тестов

```python
# Использование фикстур с областью видимости
@pytest.fixture(scope="session")
async def shared_db():
    """База данных, используемая для всех тестов в сессии."""
    # Создание БД один раз для всех тестов
    pass

@pytest.fixture(scope="function")
async def clean_db():
    """Чистая база данных для каждого теста."""
    # Очистка БД перед каждым тестом
    pass
```

## 🔧 CI/CD интеграция

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest tests/ --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Локальная проверка

```bash
# Проверка перед коммитом
make test
make lint
make format
```

## 📝 Лучшие практики

### 1. Именование тестов

```python
def test_create_checkin_type_1_on_spot():
    """Тест создания чек-ина типа 1 на споте."""
    pass

def test_create_checkin_with_invalid_spot_raises_error():
    """Тест создания чек-ина с несуществующим спотом вызывает ошибку."""
    pass
```

### 2. Структура теста

```python
def test_function_name():
    """Описание того, что тестируется."""
    # Arrange - подготовка данных
    user = User(id=123, name="Test")
    
    # Act - выполнение действия
    result = function_under_test(user)
    
    # Assert - проверка результата
    assert result is not None
    assert result.id == 123
```

### 3. Изоляция тестов

```python
@pytest.mark.asyncio
async def test_isolated():
    """Каждый тест должен быть независимым."""
    # Использование фикстур для изоляции
    # Очистка данных после теста
    pass
```

### 4. Тестирование граничных случаев

```python
def test_edge_cases():
    """Тестирование граничных случаев."""
    # Пустые данные
    # Максимальные значения
    # Неверные типы данных
    # Отсутствующие данные
    pass
```

## 🐛 Отладка тестов

### Подробный вывод

```bash
# Подробный вывод
pytest tests/ -v -s

# Остановка на первой ошибке
pytest tests/ -x

# Запуск только упавших тестов
pytest tests/ --lf
```

### Логирование в тестах

```python
import logging

def test_with_logging(caplog):
    """Тест с проверкой логов."""
    with caplog.at_level(logging.INFO):
        function_that_logs()
    
    assert "Expected log message" in caplog.text
```

## 📚 Дополнительные ресурсы

- [pytest документация](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)

---

Правильно настроенное тестирование обеспечивает надежность и стабильность WindSpotBot! 🚀