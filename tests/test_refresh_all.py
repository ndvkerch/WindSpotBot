import pytest
from src.handlers.activity import callback_refresh_all
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock
from src.services.geo import GeoService
from src.services.spot import SpotService, Spot, SpotWithDistance
from src.services.checkin import CheckinService
from src.services.weather import WeatherService
from src.services.chat import ChatService


@pytest.mark.asyncio
async def test_callback_refresh_all_no_changes():
    callback = AsyncMock()
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
    checkin_service.get_active_users.return_value = ([], [])
    weather_service.get_weather.return_value = {
        "wind_speed": 5.0,
        "wind_direction": 180,
        "wind_gusts": 7.0,
        "water_temperature": 15.0,
    }
    chat_service.get_chat_link.return_value = None
    callback.message.bot.edit_message_text.side_effect = Exception(
        "message is not modified"
    )

    # Вызов функции
    await callback_refresh_all(callback, state)

    # Проверки
    state.update_data.assert_called_with(activity_message_ids=[(12, 123)])
    callback.answer.assert_called()
