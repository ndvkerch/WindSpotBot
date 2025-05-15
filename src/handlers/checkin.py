import logging
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.services.geo import GeoService
from src.services.spot import SpotService
from src.services.checkin import CheckinService
from src.models.user import User
from src.keyboards.main import MainKeyboards
from datetime import datetime

logger = logging.getLogger(__name__)

class CheckinStates(StatesGroup):
    """Состояния для процесса чек-ина."""
    requesting_location = State()
    selecting_spot = State()
    selecting_type = State()
    selecting_duration = State()

def register_checkin_handlers(
    dp: Dispatcher,
    geo_service: GeoService,
    spot_service: SpotService,
    checkin_service: CheckinService,
):
    """Регистрация хендлеров для команды /checkin."""

    @dp.message(Command(commands=["checkin"]))
    async def cmd_checkin(message: Message, state: FSMContext, user_id: int = None):
        """Обработка команды /checkin."""
        user_id = user_id or message.from_user.id
        logger.info(f"Команда /checkin от пользователя {user_id}")
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
                await message.answer(
                    "🤙 Йо, споты не найдены! Добавь новый через /add_spot! 🪁"
                )
                return
            kb = MainKeyboards.get_spots_list(nearby_spots)
            await state.update_data(latitude=latitude, longitude=longitude)
            await message.answer("🏄‍♂️ Выбери спот для чек-ина:", reply_markup=kb)
            await state.set_state(CheckinStates.selecting_spot)
        else:
            await geo_service.request_location(message, state, user_id)
            await state.set_state(CheckinStates.requesting_location)

    @dp.message(CheckinStates.requesting_location)
    async def process_checkin_location(message: Message, state: FSMContext):
        """Обработка геолокации для чек-ина."""
        user_id = message.from_user.id
        logger.info(f"Обработка геолокации для чек-ина от пользователя {user_id}")
        if not message.location:
            logger.warning("Получен неверный тип контента: не геолокация")
            await message.answer("🤙 Йо, отправь геолокацию, бро! 📍")
            return
        latitude = message.location.latitude
        longitude = message.location.longitude
        await geo_service.cache_location(user_id, latitude, longitude)
        logger.info(f"Получена геолокация: ({latitude}, {longitude})")
        spots = await spot_service.get_all_spots()
        nearby_spots = await geo_service.get_nearby_spots(spots, latitude, longitude)
        if not nearby_spots:
            await message.answer(
                "🤙 Йо, споты не найдены! Добавь новый через /add_spot! 🪁"
            )
            await state.clear()
            return
        kb = MainKeyboards.get_spots_list(nearby_spots)
        await state.update_data(latitude=latitude, longitude=longitude)
        await message.answer("🏄‍♂️ Выбери спот для чек-ина:", reply_markup=kb)
        await state.set_state(CheckinStates.selecting_spot)

    @dp.callback_query(
        lambda c: c.data and c.data.startswith("spot:"), CheckinStates.selecting_spot
    )
    async def callback_spot(callback: CallbackQuery, state: FSMContext):
        """Обработка выбора спота."""
        user_id = callback.from_user.id
        logger.info(f"Выбор спота: {callback.data} пользователем {user_id}")
        try:
            spot_id = int(callback.data.split(":", 1)[1])
            spot = await spot_service.get_spot_by_id(spot_id)
            if not spot:
                await callback.message.edit_text(
                    f"🤙 Спот с ID {spot_id} не найден, бро! 😕"
                )
                await state.clear()
                return
            kb = MainKeyboards.get_checkin_types()
            await callback.message.edit_text(
                f"🏄‍♂️ Йо, ты выбрал '{spot.name}'! Какой вайб? 💨", reply_markup=kb
            )
            await state.update_data(spot_id=spot.id, spot_name=spot.name)
            await state.set_state(CheckinStates.selecting_type)
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_spot: {e}")
            await callback.message.edit_text(f"😕 Ошибка при выборе спота: {str(e)}")
            await state.clear()

    @dp.callback_query(
        lambda c: c.data and c.data.startswith("checkin:"), CheckinStates.selecting_type
    )
    async def callback_checkin_type(callback: CallbackQuery, state: FSMContext):
        """Обработка выбора типа чек-ина."""
        user_id = callback.from_user.id
        logger.info(f"Выбор типа чек-ина: {callback.data} пользователем {user_id}")
        try:
            data = await state.get_data()
            spot_id = data.get("spot_id")
            spot_name = data.get("spot_name")
            if not spot_id:
                await callback.message.edit_text("😕 Ошибка: спот не выбран, бро!")
                await state.clear()
                return
            checkin_type = int(callback.data.split(":", 1)[1])
            if checkin_type == 1:  # На месте
                kb = MainKeyboards.get_duration_options()
                await callback.message.edit_text(
                    f"✅ Йо, ты на '{spot_name}'! Лови вайб! 🏄‍♂️\nСколько тусить будешь?",
                    reply_markup=kb,
                )
                await state.update_data(checkin_type=checkin_type)
                await state.set_state(CheckinStates.selecting_duration)
            else:
                # Для типов 2 и 3 используем фиксированную длительность
                user = User(
                    id=user_id,
                    name=callback.from_user.full_name,
                    username=callback.from_user.username,
                )
                success = await checkin_service.create_checkin(
                    user, spot_id, checkin_type, duration=3600
                )
                await state.clear()
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_checkin_type: {e}")
            await callback.message.edit_text(f"😕 Ошибка при чек-ине: {str(e)}")
            await state.clear()

    @dp.callback_query(
        lambda c: c.data and c.data.startswith("duration:"),
        CheckinStates.selecting_duration,
    )
    async def callback_duration(callback: CallbackQuery, state: FSMContext):
        """Обработка выбора длительности чек-ина."""
        user_id = callback.from_user.id
        logger.info(f"Выбор длительности: {callback.data} пользователем {user_id}")
        try:
            data = await state.get_data()
            spot_id = data.get("spot_id")
            checkin_type = data.get("checkin_type")
            if not spot_id or not checkin_type:
                await callback.message.edit_text("😕 Ошибка: данные не найдены, бро!")
                await state.clear()
                return
            duration_hours = int(callback.data.split(":", 1)[1])
            duration_seconds = duration_hours * 3600
            user = User(
                id=user_id,
                name=callback.from_user.full_name,
                username=callback.from_user.username,
            )
            success = await checkin_service.create_checkin(
                user, spot_id, checkin_type, duration=duration_seconds
            )
            await state.clear()
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_duration: {e}")
            await callback.message.edit_text(
                f"😕 Ошибка при выборе длительности: {str(e)}"
            )
            await state.clear()

    @dp.callback_query(lambda c: c.data and c.data.startswith("leave_spot:"))
    async def callback_leave_spot(callback: CallbackQuery, state: FSMContext):
        """Обработка кнопки 'Покинуть спот'."""
        user_id = callback.from_user.id
        logger.info(
            f"Нажата кнопка 'Покинуть спот': {callback.data} от пользователя {user_id}"
        )
        try:
            checkin_id = int(callback.data.split(":", 1)[1])
            checkin = await checkin_service.checkin_repo.get_by_id(checkin_id)
            if not checkin or not checkin.active:
                await callback.message.edit_text("😕 Чек-ин не найден или не активен, бро!")
                await state.clear()
                return
            spot = await checkin_service.spot_service.get_spot_by_id(checkin.spot_id)
            if not spot:
                await callback.message.edit_text("😕 Спот не найден, бро!")
                await state.clear()
                return
            # Проверяем, просрочен ли чек-ин
            now = datetime.utcnow()
            is_expired = checkin.active_until and checkin.active_until < now
            update_duration = not is_expired
            await checkin_service.checkin_repo.deactivate_checkin(checkin_id, update_duration=update_duration)
            user = User(
                id=user_id,
                name=callback.from_user.full_name,
                username=callback.from_user.username,
            )
            await checkin_service.notification_service.send_checkout_notification(
                user, spot.name
            )
            await checkin_service.notification_service.send_spot_checkout_notification(
                user, spot.name
            )
            kb = await MainKeyboards.get_main_menu(user_id, checkin_service.checkin_repo)
            await callback.message.edit_text(
                f"🚪 Йо, ты покинул '{spot.name}'! 💨 Лови главное меню! 🏄‍♂️",
                reply_markup=kb,
            )
            logger.info(
                f"Пользователь {user_id} покинул спот '{spot.name}' (чек-ин #{checkin_id})"
            )
            await state.clear()
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_leave_spot: {e}")
            await callback.message.edit_text(f"😕 Ошибка при покидании спота: {str(e)}")
            await state.clear()

    @dp.callback_query(lambda c: c.data == "back_to_location")
    async def callback_back_to_location(callback: CallbackQuery, state: FSMContext):
        """Обработка возврата к запросу геолокации."""
        user_id = callback.from_user.id
        logger.info(f"Нажата кнопка 'Назад' от пользователя {user_id}")
        await state.clear()
        await geo_service.request_location(callback.message, state, user_id)
        await state.set_state(CheckinStates.requesting_location)
        await callback.message.edit_text("🤙 Йо, отправь геолокацию, бро! 📍")
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "back_to_spots")
    async def callback_back_to_spots(callback: CallbackQuery, state: FSMContext):
        """Обработка возврата к выбору спота."""
        user_id = callback.from_user.id
        logger.info(f"Нажата кнопка 'Назад' от пользователя {user_id}")
        data = await state.get_data()
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        if latitude and longitude:
            spots = await spot_service.get_all_spots()
            nearby_spots = await geo_service.get_nearby_spots(
                spots, latitude, longitude
            )
            if not nearby_spots:
                await callback.message.edit_text(
                    "🤙 Йо, споты не найдены! Добавь новый через /add_spot! 🪁"
                )
                await state.clear()
                return
            kb = MainKeyboards.get_spots_list(nearby_spots)
            await callback.message.edit_text(
                "🏄‍♂️ Выбери спот для чек-ина:", reply_markup=kb
            )
            await state.set_state(CheckinStates.selecting_spot)
        else:
            await callback.message.edit_text(
                "😕 Геолокация не найдена. Отправь заново, бро!"
            )
            await geo_service.request_location(callback.message, state, user_id)
            await state.set_state(CheckinStates.requesting_location)
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "main_menu")
    async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
        """Обработка возврата в главное меню."""
        user_id = callback.from_user.id
        logger.info(f"Нажата кнопка 'В главное меню' от пользователя {user_id}")
        await state.clear()
        kb = await MainKeyboards.get_main_menu(user_id, checkin_service.checkin_repo)
        await callback.message.edit_text(
            "🤙 Йо, бро! Лови главное меню WindSpotBot! 🏄‍♂️\n"
            "Найди спот, чек-инься или туси в @WindSpotRU! 💨",
            reply_markup=kb,
        )
        await callback.answer()
