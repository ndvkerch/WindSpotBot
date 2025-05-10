import pytest
from src.bot import show_activity
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock
from src.services.spot import SpotService
from src.services.checkin import CheckinService
from src.services.weather import WeatherService
from src.services.chat import ChatService


@pytest.mark.asyncio
async def test_show_activity_no_spots():
    message = AsyncMock()
    spot_service = AsyncMock(spec=SpotService)
    checkin_service = AsyncMock(spec=CheckinService)
    weather_service = AsyncMock(spec=WeatherService)
    chat_service = AsyncMock(spec=ChatService)
    state = AsyncMock(spec=FSMContext)
    spot_service.get_all_spots.return_value = []
    await show_activity(
        message,
        45.0,
        36.0,
        spot_service,
        checkin_service,
        weather_service,
        chat_service,
        7395203712,
        state,
    )
    message.answer.assert_called_with("Активные споты не найдены.")
