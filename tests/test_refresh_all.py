import pytest
from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock
from src.handlers.activity import register_activity_handlers
from src.services.geo import GeoService
from src.services.spot import SpotService, Spot, SpotWithDistance
from src.services.checkin import CheckinService
from src.services.weather import WeatherService
from src.services.chat import ChatService
from src.keyboards.main import MainKeyboards


@pytest.mark.asyncio
async def test_callback_refresh_all_no_changes():
    # Создаём моки
    callback = AsyncMock(spec=CallbackQuery)
    callback.data = "refresh_all"
    callback.from_user.id = 7395203712
    state = AsyncMock(spec=FSMContext)
    geo_service = AsyncMock(spec=GeoService)
    spot_service = AsyncMock(spec=SpotService)
    checkin_service = AsyncMock(spec=CheckinService)
    weather_service = AsyncMock(spec=WeatherService)
    chat_service = AsyncMock(spec=ChatService)

    # Настройка моков
    geo_service.get_cached_location.return_value = (45.0, 36.0)
    state.get_data.return_value = {"activity_message_ids": [(12, 123)]}
    spot_service.get_all_spots.return_value = [
        Spot(
            id=12,
            name="Test Spot",
            latitude=45.0,
            longitude=36.0,
            created_by=7395203712,
        )
    ]
    geo_service.get_nearby_spots.return_value = [
        SpotWithDistance(
            spot=Spot(
                id=12,
                name="Test Spot",
                latitude=45.0,
                longitude=36.0,
                created_by=7395203712,
            ),
            distance=0.0,
        )
    ]
    checkin_service.get_active_users.return_value = ([], [])  # Никого нет
    weather_service.get_weather.return_value = {
        "wind_speed": 5.0,
        "wind_direction": 180,
        "wind_gusts": 7.0,
        "water_temperature": 15.0,
    }
    weather_service.wind_direction_to_text.return_value = "Южный"
    chat_service.get_chat_link.return_value = None
    callback.message.bot.edit_message_text.side_effect = Exception(
        "message is not modified"
    )
    MainKeyboards.get_activity_controls = AsyncMock(return_value="mocked_keyboard")

    # Регистрируем хендлеры
    dp = Dispatcher()
    register_activity_handlers(
        dp, geo_service, spot_service, checkin_service, weather_service, chat_service
    )

    # Вызываем callback хендлер
    await dp.feed_update(bot=callback.message.bot, update={"callback_query": callback})

    # Проверки
    state.update_data.assert_called_with(activity_message_ids=[(12, 123)])
    callback.answer.assert_called()


@pytest.mark.asyncio
async def test_callback_refresh_all_planning_info():
    # Создаём моки
    callback = AsyncMock(spec=CallbackQuery)
    callback.data = "refresh_all"
    callback.from_user.id = 7395203712
    state = AsyncMock(spec=FSMContext)
    geo_service = AsyncMock(spec=GeoService)
    spot_service = AsyncMock(spec=SpotService)
    checkin_service = AsyncMock(spec=CheckinService)
    weather_service = AsyncMock(spec=WeatherService)
    chat_service = AsyncMock(spec=ChatService)

    # Настройка моков
    geo_service.get_cached_location.return_value = (45.0, 36.0)
    state.get_data.return_value = {"activity_message_ids": [(12, 123)]}
    spot_service.get_all_spots.return_value = [
        Spot(
            id=12,
            name="Test Spot",
            latitude=45.0,
            longitude=36.0,
            created_by=7395203712,
        )
    ]
    geo_service.get_nearby_spots.return_value = [
        SpotWithDistance(
            spot=Spot(
                id=12,
                name="Test Spot",
                latitude=45.0,
                longitude=36.0,
                created_by=7395203712,
            ),
            distance=0.0,
        )
    ]
    checkin_service.get_active_users.return_value = ([], [1, 2])  # Есть планирующие
    weather_service.get_weather.return_value = {
        "wind_speed": 5.0,
        "wind_direction": 180,
        "wind_gusts": 7.0,
        "water_temperature": 15.0,
    }
    weather_service.wind_direction_to_text.return_value = "Южный"
    chat_service.get_chat_link.return_value = None
    callback.message.bot.edit_message_text.side_effect = Exception(
        "message is not modified"
    )
    MainKeyboards.get_activity_controls = AsyncMock(return_value="mocked_keyboard")

    # Регистрируем хендлеры
    dp = Dispatcher()
    register_activity_handlers(
        dp, geo_service, spot_service, checkin_service, weather_service, chat_service
    )

    # Вызываем callback хендлер
    await dp.feed_update(bot=callback.message.bot, update={"callback_query": callback})

    # Проверки
    state.update_data.assert_called_with(activity_message_ids=[(12, 123)])
    callback.answer.assert_called()
