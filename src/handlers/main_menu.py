import logging
from aiogram import Dispatcher
from aiogram.types import CallbackQuery, Message, Location
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.services.geo import GeoService
from src.services.spot import SpotService
from src.services.checkin import CheckinService
from src.services.weather import WeatherService
from src.services.chat import ChatService
from src.keyboards.main import MainKeyboards
from src.repositories.user import UserRepository
from src.handlers.checkin import CheckinStates
from src.repositories.checkin import CheckinRepository

logger = logging.getLogger(__name__)

class SpotsStates(StatesGroup):
    """Состояния для просмотра спотов."""
    requesting_location = State()

class AddSpotStates(StatesGroup):
    """Состояния для добавления спота."""
    entering_name = State()

class ActivityStates(StatesGroup):
    """Состояния для активности."""
    requesting_location = State()

def register_main_menu_handlers(dp: Dispatcher):
    """Регистрация обработчиков для callback-запросов главного меню."""

    @dp.callback_query(lambda c: c.data == "checkin")
    async def callback_checkin(callback: CallbackQuery, state: FSMContext, geo_service: GeoService, spot_service: SpotService):
        """Обработка нажатия кнопки 'Чек-ин'."""
        user_id = callback.from_user.id
        logger.info(f"Callback 'checkin' от пользователя {user_id}")
        await state.clear()
        cached_location = await geo_service.get_cached_location(user_id)
        if cached_location:
            latitude, longitude = cached_location
            logger.info(f"Использован кэш: ({latitude}, {longitude})")
            spots = await spot_service.get_all_spots()
            nearby_spots = await geo_service.get_nearby_spots(
                spots, latitude, longitude
            )
            if not nearby_spots:
                await callback.message.answer(
                    "Споты не найдены. Добавьте споты через /add_spot."
                )
                await callback.answer()
                return
            kb = MainKeyboards.get_spots_list(nearby_spots)
            await state.update_data(latitude=latitude, longitude=longitude)
            await callback.message.answer("Выберите спот для чек-ина:", reply_markup=kb)
            await state.set_state(CheckinStates.selecting_spot)
        else:
            await geo_service.request_location(callback.message, state, user_id)
            await state.set_state(CheckinStates.requesting_location)
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "activity")
    async def callback_activity(
        callback: CallbackQuery,
        state: FSMContext,
        geo_service: GeoService,
        spot_service: SpotService,
        checkin_service: CheckinService,
        weather_service: WeatherService,
        chat_service: ChatService,
    ):
        """Обработка нажатия кнопки 'Активность'."""
        user_id = callback.from_user.id
        logger.info(f"Callback 'activity' от пользователя {user_id}")
        await state.clear()
        cached_location = await geo_service.get_cached_location(user_id)
        if cached_location:
            latitude, longitude = cached_location
            logger.info(f"Использован кэш: ({latitude}, {longitude})")
            from src.handlers.activity import show_activity
            await show_activity(
                callback.message,
                latitude,
                longitude,
                spot_service,
                checkin_service,
                weather_service,
                chat_service,
                user_id,
                state,
                geo_service,
            )
        else:
            await geo_service.request_location(callback.message, state, user_id)
            await state.set_state(ActivityStates.requesting_location)
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "spots")
    async def callback_spots(callback: CallbackQuery, state: FSMContext, geo_service: GeoService, spot_service: SpotService):
        """Обработка нажатия кнопки 'Ближайшие споты'."""
        user_id = callback.from_user.id
        logger.info(f"Callback 'spots' от пользователя {user_id}")
        await state.clear()
        cached_location = await geo_service.get_cached_location(user_id)
        if cached_location:
            latitude, longitude = cached_location
            logger.info(f"Использован кэш: ({latitude}, {longitude})")
            spots = await spot_service.get_all_spots()
            nearby_spots = await geo_service.get_nearby_spots(
                spots, latitude, longitude
            )
            if not nearby_spots:
                await callback.message.answer(
                    "Споты не найдены. Добавьте споты через /add_spot."
                )
            else:
                kb = MainKeyboards.get_spots_list(nearby_spots)
                await callback.message.answer("Ближайшие споты:", reply_markup=kb)
        else:
            await geo_service.request_location(callback.message, state, user_id)
            await state.set_state(SpotsStates.requesting_location)
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "add_spot")
    async def callback_add_spot(callback: CallbackQuery, state: FSMContext):
        """Обработка нажатия кнопки 'Добавить спот'."""
        user_id = callback.from_user.id
        logger.info(f"Callback 'add_spot' от пользователя {user_id}")
        await state.clear()
        await callback.message.answer("Введите название спота:")
        await state.set_state(AddSpotStates.entering_name)
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "main_menu")
    async def callback_main_menu(callback: CallbackQuery, state: FSMContext, checkin_repo: CheckinRepository):
        """Обработка нажатия кнопки 'В главное меню'."""
        user_id = callback.from_user.id
        logger.info(f"Callback 'main_menu' от пользователя {user_id}")
        await state.clear()
        kb = await MainKeyboards.get_main_menu(user_id, checkin_repo)
        await callback.message.answer("Главное меню:", reply_markup=kb)
        await callback.answer()

    @dp.message(ActivityStates.requesting_location)
    async def process_activity_location(
        message: Message,
        state: FSMContext,
        geo_service: GeoService,
        spot_service: SpotService,
        checkin_service: CheckinService,
        weather_service: WeatherService,
        chat_service: ChatService,
    ):
        """Обработка геолокации для активности."""
        user_id = message.from_user.id
        logger.info(f"Получена геолокация для активности от пользователя {user_id}")
        if not message.location:
            await message.answer("Пожалуйста, отправьте геолокацию.")
            return
        latitude = message.location.latitude
        longitude = message.location.longitude
        await geo_service.cache_location(user_id, latitude, longitude)
        from src.handlers.activity import show_activity
        await show_activity(
            message,
            latitude,
            longitude,
            spot_service,
            checkin_service,
            weather_service,
            chat_service,
            user_id,
            state,
            geo_service,
        )
        await state.clear()

    @dp.message(SpotsStates.requesting_location)
    async def process_spots_location(
        message: Message,
        state: FSMContext,
        user_repo: UserRepository,
        geo_service: GeoService,
    ):
        """Обработка геолокации для ближайших спотов."""
        user_id = message.from_user.id
        logger.info(f"Получена геолокация для спотов от пользователя {user_id}")
        if not message.location:
            await message.answer("Пожалуйста, отправьте геолокацию.")
            return
        latitude = message.location.latitude
        longitude = message.location.longitude
        await geo_service.cache_location(user_id, latitude, longitude)
        timezone = await geo_service.get_timezone(latitude, longitude)
        if timezone:
            await user_repo.create(
                user_id=user_id,
                name=message.from_user.full_name,
                username=message.from_user.username,
                timezone=timezone,
            )
            logger.info(f"Часовой пояс {timezone} сохранен для пользователя {user_id}")
        spots = await spot_service.get_all_spots()
        nearby_spots = await geo_service.get_nearby_spots(spots, latitude, longitude)
        if not nearby_spots:
            await message.answer("Споты не найдены. Добавьте споты через /add_spot.")
        else:
            kb = MainKeyboards.get_spots_list(nearby_spots)
            await message.answer("Ближайшие споты:", reply_markup=kb)
        await state.clear()
