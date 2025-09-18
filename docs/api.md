# API WindSpotBot 📡

WindSpotBot предоставляет REST API для интеграции с внешними системами и мобильными приложениями. API построен на основе FastAPI и использует Pydantic модели для валидации данных.

## 🚀 Быстрый старт

### Базовый URL
```
https://api.windspotbot.com/v1
```

### Аутентификация
```http
Authorization: Bearer YOUR_API_TOKEN
```

### Формат данных
Все запросы и ответы используют JSON формат.

## 📋 Эндпоинты

### Пользователи

#### GET /users/me
Получение информации о текущем пользователе.

**Ответ:**
```json
{
  "id": 123456789,
  "name": "Иван Иванов",
  "username": "ivan_ivanov",
  "timezone": "Europe/Moscow",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### PUT /users/me
Обновление информации о пользователе.

**Запрос:**
```json
{
  "name": "Иван Иванов",
  "timezone": "Europe/Moscow"
}
```

### Споты

#### GET /spots
Получение списка спотов.

**Параметры запроса:**
- `lat` (float) - широта
- `lon` (float) - долгота
- `limit` (int, optional) - лимит результатов (по умолчанию 10)
- `radius` (int, optional) - радиус поиска в метрах (по умолчанию 5000)

**Ответ:**
```json
{
  "spots": [
    {
      "id": 1,
      "name": "Должанка",
      "latitude": 46.6333,
      "longitude": 37.8000,
      "description": "Популярный спот для кайтсерфинга",
      "distance": 2.5,
      "created_by": 123456789
    }
  ],
  "total": 1
}
```

#### GET /spots/{spot_id}
Получение информации о конкретном споте.

**Ответ:**
```json
{
  "id": 1,
  "name": "Должанка",
  "latitude": 46.6333,
  "longitude": 37.8000,
  "description": "Популярный спот для кайтсерфинга",
  "created_by": 123456789,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### POST /spots
Создание нового спота.

**Запрос:**
```json
{
  "name": "Новый спот",
  "latitude": 46.6333,
  "longitude": 37.8000,
  "description": "Описание спота"
}
```

**Ответ:**
```json
{
  "id": 2,
  "name": "Новый спот",
  "latitude": 46.6333,
  "longitude": 37.8000,
  "description": "Описание спота",
  "created_by": 123456789,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Чек-ины

#### GET /checkins
Получение чек-инов пользователя.

**Параметры запроса:**
- `type` (int, optional) - тип чек-ина (1: на месте, 2: прибуду, 3: планирую)
- `active` (boolean, optional) - только активные чек-ины
- `limit` (int, optional) - лимит результатов

**Ответ:**
```json
{
  "checkins": [
    {
      "id": 1,
      "user_id": 123456789,
      "spot_id": 1,
      "type": 1,
      "duration": 3600,
      "created_at": "2024-01-15T10:30:00Z",
      "active_until": "2024-01-15T11:30:00Z",
      "active": true,
      "spot": {
        "id": 1,
        "name": "Должанка",
        "latitude": 46.6333,
        "longitude": 37.8000
      }
    }
  ],
  "total": 1
}
```

#### POST /checkins
Создание нового чек-ина.

**Запрос:**
```json
{
  "spot_id": 1,
  "type": 1,
  "duration": 3600
}
```

**Ответ:**
```json
{
  "id": 1,
  "user_id": 123456789,
  "spot_id": 1,
  "type": 1,
  "duration": 3600,
  "created_at": "2024-01-15T10:30:00Z",
  "active_until": "2024-01-15T11:30:00Z",
  "active": true
}
```

#### PUT /checkins/{checkin_id}
Обновление чек-ина.

**Запрос:**
```json
{
  "duration": 7200,
  "active": false
}
```

#### DELETE /checkins/{checkin_id}
Удаление чек-ина.

**Ответ:**
```json
{
  "message": "Чек-ин успешно удален"
}
```

### Активность

#### GET /spots/{spot_id}/activity
Получение активности на споте.

**Ответ:**
```json
{
  "spot": {
    "id": 1,
    "name": "Должанка",
    "latitude": 46.6333,
    "longitude": 37.8000
  },
  "weather": {
    "wind_speed": 5.2,
    "temperature": 22.0,
    "water_temperature": 18.5,
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "users_on_spot": [
    {
      "id": 123456789,
      "name": "Иван Иванов",
      "checkin_type": 1,
      "checkin_duration": 3600,
      "checkin_created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "users_coming": [
    {
      "id": 987654321,
      "name": "Петр Петров",
      "checkin_type": 2,
      "planned_at": "2024-01-15T12:00:00Z"
    }
  ],
  "total_active": 1,
  "total_coming": 1
}
```

### Подписки

#### GET /subscriptions
Получение подписок пользователя.

**Ответ:**
```json
{
  "subscriptions": [
    {
      "spot_name": "Должанка",
      "event_type": "checkin",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1
}
```

#### POST /subscriptions
Создание подписки.

**Запрос:**
```json
{
  "spot_name": "Должанка",
  "event_type": "checkin"
}
```

**Ответ:**
```json
{
  "message": "Подписка успешно создана"
}
```

#### DELETE /subscriptions
Удаление подписки.

**Запрос:**
```json
{
  "spot_name": "Должанка",
  "event_type": "checkin"
}
```

### Погода

#### GET /weather
Получение погодных данных.

**Параметры запроса:**
- `lat` (float) - широта
- `lon` (float) - долгота

**Ответ:**
```json
{
  "wind_speed": 5.2,
  "wind_direction": 180,
  "temperature": 22.0,
  "water_temperature": 18.5,
  "humidity": 65,
  "pressure": 1013.25,
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## 🔐 Аутентификация

### Получение токена

```http
POST /auth/token
Content-Type: application/json

{
  "telegram_id": 123456789,
  "telegram_username": "ivan_ivanov"
}
```

**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Обновление токена

```http
POST /auth/refresh
Authorization: Bearer YOUR_REFRESH_TOKEN
```

## 📊 Коды ответов

| Код | Описание |
|-----|----------|
| 200 | Успешный запрос |
| 201 | Ресурс создан |
| 400 | Неверный запрос |
| 401 | Не авторизован |
| 403 | Доступ запрещен |
| 404 | Ресурс не найден |
| 422 | Ошибка валидации |
| 500 | Внутренняя ошибка сервера |

## 🚨 Обработка ошибок

### Формат ошибки

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Ошибка валидации данных",
    "details": {
      "field": "latitude",
      "message": "Значение должно быть числом"
    }
  }
}
```

### Коды ошибок

| Код | Описание |
|-----|----------|
| `VALIDATION_ERROR` | Ошибка валидации данных |
| `AUTHENTICATION_ERROR` | Ошибка аутентификации |
| `AUTHORIZATION_ERROR` | Ошибка авторизации |
| `RESOURCE_NOT_FOUND` | Ресурс не найден |
| `DUPLICATE_RESOURCE` | Ресурс уже существует |
| `RATE_LIMIT_EXCEEDED` | Превышен лимит запросов |
| `INTERNAL_ERROR` | Внутренняя ошибка сервера |

## 📈 Лимиты и квоты

### Лимиты запросов

- **Базовый лимит**: 1000 запросов в час
- **Премиум лимит**: 10000 запросов в час
- **Burst лимит**: 100 запросов в минуту

### Лимиты данных

- **Максимум спотов**: 1000 на пользователя
- **Максимум чек-инов**: 10000 на пользователя
- **Максимум подписок**: 50 на пользователя

## 🔄 Webhooks

### Настройка webhook

```http
POST /webhooks
Authorization: Bearer YOUR_API_TOKEN
Content-Type: application/json

{
  "url": "https://your-app.com/webhook",
  "events": ["checkin.created", "checkin.updated", "checkin.deleted"]
}
```

### События

- `checkin.created` - создан новый чек-ин
- `checkin.updated` - обновлен чек-ин
- `checkin.deleted` - удален чек-ин
- `spot.created` - создан новый спот
- `weather.updated` - обновлены погодные данные

### Формат webhook

```json
{
  "event": "checkin.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "checkin": {
      "id": 1,
      "user_id": 123456789,
      "spot_id": 1,
      "type": 1,
      "duration": 3600,
      "created_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

## 🛠️ SDK и библиотеки

### Python SDK

```python
from windspotbot import WindSpotBotAPI

api = WindSpotBotAPI(api_key="your_api_key")

# Получение спотов
spots = await api.spots.get_nearby(lat=46.6333, lon=37.8000)

# Создание чек-ина
checkin = await api.checkins.create(spot_id=1, type=1, duration=3600)
```

### JavaScript SDK

```javascript
import { WindSpotBotAPI } from 'windspotbot-js';

const api = new WindSpotBotAPI('your_api_key');

// Получение спотов
const spots = await api.spots.getNearby(46.6333, 37.8000);

// Создание чек-ина
const checkin = await api.checkins.create({
  spot_id: 1,
  type: 1,
  duration: 3600
});
```

## 📚 Дополнительные ресурсы

- [Postman коллекция](https://api.windspotbot.com/docs/postman)
- [OpenAPI спецификация](https://api.windspotbot.com/docs/openapi.json)
- [Интерактивная документация](https://api.windspotbot.com/docs)
- [Примеры кода](https://github.com/windspotbot/examples)

## 🔄 Версионирование

API использует семантическое версионирование. Текущая версия: `v1`.

### Изменения в API

- **Major версия** - несовместимые изменения
- **Minor версия** - новая функциональность (обратно совместимая)
- **Patch версия** - исправления ошибок

### Поддержка версий

- **v1** - поддерживается до 2025-12-31
- **v2** - планируется к релизу в Q2 2025

---

WindSpotBot API предоставляет мощный и гибкий интерфейс для интеграции с внешними системами! 🚀