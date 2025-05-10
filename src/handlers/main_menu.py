import logging
from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.services.geo import GeoService
from src.services.spot import SpotService
from src.services.checkin import CheckinService
from src.keyboards.main import MainKeyboards

logger = logging.getLogger(__name__)


class SpotsStates(StatesGroup):
    """Состояния для просмотра спотов."""

    requesting_location = State()


class CheckinStates(StatesGroup):
    """Состояния для процесса чек-ина."""

    requesting_location = State()


class AddSpotStates(StatesGroup):
    """Состояния для добавления спота."""

    entering_name = State()


def register_main_menu_handlers(
    dp: Dispatcher,
    geo_service: GeoService,
    spot_service: SpotService,
    checkin_service: CheckinService,
):
    """Регистрация обработчиков для callback-запросов главного меню."""

    @dp.callback_query(lambda c: c.data == "activity")
    async def callback_activity(callback: CallbackQuery, state: FSMContext):
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
                None,  # weather_service, можно добавить позже
                None,  # chat_service, можно добавить позже
                user_id,
                state,
                geo_service,
            )
        else:
            await geo_service.request_location(callback.message, state, user_id)
            await state.set_state(State("ActivityStates:requesting_location"))
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "spots")
    async def callback_spots(callback: CallbackQuery, state: FSMContext):
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

    @dp.callback_query(lambda c: c.data == "checkin")
    async def callback_checkin(callback: CallbackQuery, state: FSMContext):
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
            else:
                await state.update_data(latitude=latitude, longitude=longitude)
                kb = MainKeyboards.get_spots_list(nearby_spots)
                await callback.message.answer("Выберите спот:", reply_markup=kb)
                await state.set_state(CheckinStates.requesting_location)
        else:
            await geo_service.request_location(callback.message, state, user_id)
            await state.set_state(CheckinStates.requesting_location)
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
    async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
        """Обработка нажатия кнопки 'В главное меню'."""
        user_id = callback.from_user.id
        logger.info(f"Callback 'main_menu' от пользователя {user_id}")
        await state.clear()
        kb = MainKeyboards.get_main_menu()
        await callback.message.answer("Главное меню:", reply_markup=kb)
        await callback.answer()
