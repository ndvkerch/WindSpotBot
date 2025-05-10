import logging
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from src.services.geo import GeoService
from src.services.spot import SpotService
from src.services.checkin import CheckinService
from src.models.user import User
from src.keyboards.main import MainKeyboards

logger = logging.getLogger(__name__)


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
                    "Споты не найдены. Добавьте споты через /add_spot."
                )
                return
            kb = MainKeyboards.get_spots_list(nearby_spots)
            await state.update_data(latitude=latitude, longitude=longitude)
            await message.answer("Выберите спот для чек-ина:", reply_markup=kb)
            await state.set_state(State("CheckinStates:selecting_spot"))
        else:
            await geo_service.request_location(message, state, user_id)
            await state.set_state(State("CheckinStates:requesting_location"))

    @dp.message(State("CheckinStates:requesting_location"))
    async def process_checkin_location(message: Message, state: FSMContext):
        """Обработка геолокации для чек-ина."""
        user_id = message.from_user.id
        logger.info(f"Обработка геолокации для чек-ина от пользователя {user_id}")
        if message.content_type not in ["location", "venue"]:
            logger.warning(f"Получен неверный тип контента: {message.content_type}")
            await message.answer("Пожалуйста, отправьте геолокацию или место.")
            return
        if message.content_type == "location":
            location = await geo_service.process_location(message, state)
        else:
            latitude = message.venue.location.latitude
            longitude = message.venue.location.longitude
            await geo_service.cache_location(user_id, latitude, longitude)
            location = (latitude, longitude)
        if location:
            latitude, longitude = location
            logger.info(f"Получена геолокация: ({latitude}, {longitude})")
            spots = await spot_service.get_all_spots()
            nearby_spots = await geo_service.get_nearby_spots(
                spots, latitude, longitude
            )
            if not nearby_spots:
                await message.answer(
                    "Споты не найдены. Добавьте споты через /add_spot."
                )
                return
            kb = MainKeyboards.get_spots_list(nearby_spots)
            await state.update_data(latitude=latitude, longitude=longitude)
            await message.answer("Выберите спот для чек-ина:", reply_markup=kb)
            await state.set_state(State("CheckinStates:selecting_spot"))
        else:
            logger.error("Не удалось обработать геолокацию")
            await message.answer("Ошибка при обработке геолокации.")

    @dp.callback_query(
        lambda c: c.data and c.data.startswith("spot:"),
        State("CheckinStates:selecting_spot"),
    )
    async def callback_spot(callback: CallbackQuery, state: FSMContext):
        """Обработка выбора спота."""
        user_id = callback.from_user.id
        logger.info(f"Выбор спота: {callback.data} пользователем {user_id}")
        try:
            spot_id = int(callback.data.split(":", 1)[1])
            spot = await spot_service.get_spot_by_id(spot_id)
            if not spot:
                await callback.message.edit_text(f"Спот с ID {spot_id} не найден.")
                return
            kb = MainKeyboards.get_checkin_types()
            await callback.message.edit_text(
                f"Вы выбрали спот '{spot.name}'. Тип чек-ина:", reply_markup=kb
            )
            await state.update_data(spot_id=spot.id)
            await state.set_state(State("CheckinStates:selecting_type"))
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_spot: {e}")
            await callback.message.edit_text(f"Ошибка при выборе спота: {str(e)}")

    @dp.callback_query(
        lambda c: c.data and c.data.startswith("checkin:"),
        State("CheckinStates:selecting_type"),
    )
    async def callback_checkin(callback: CallbackQuery, state: FSMContext):
        """Обработка чек-ина."""
        user_id = callback.from_user.id
        logger.info(f"Выбор типа чек-ина: {callback.data} пользователем {user_id}")
        try:
            data = await state.get_data()
            spot_id = data.get("spot_id")
            if not spot_id:
                await callback.message.edit_text("Ошибка: спот не выбран.")
                return
            checkin_type = int(callback.data.split(":", 1)[1])
            user = User(
                id=user_id,
                name=callback.from_user.full_name,
                username=callback.from_user.username,
            )
            checkin_id = await checkin_service.create_checkin(
                user, spot_id, checkin_type, duration=3600
            )
            spot = await spot_service.get_spot_by_id(spot_id)
            if checkin_id:
                await callback.message.edit_text(
                    f"Чек-ин на споте '{spot.name}' успешно создан!"
                )
            else:
                await callback.message.edit_text(
                    f"Ошибка при создании чек-ина на споте '{spot.name}'."
                )
            await state.clear()
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_checkin: {e}")
            await callback.message.edit_text(f"Ошибка при чек-ине: {str(e)}")
            await state.clear()

    @dp.callback_query(lambda c: c.data == "back_to_location")
    async def callback_back_to_location(callback: CallbackQuery, state: FSMContext):
        """Обработка возврата к запросу геолокации."""
        user_id = callback.from_user.id
        logger.info(f"Нажата кнопка 'Назад' от пользователя {user_id}")
        await state.clear()
        await geo_service.request_location(callback.message, state, user_id)
        await state.set_state(State("CheckinStates:requesting_location"))
        await callback.message.edit_text("Пожалуйста, отправьте геолокацию.")
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
                    "Споты не найдены. Добавьте споты через /add_spot."
                )
                await state.clear()
                return
            kb = MainKeyboards.get_spots_list(nearby_spots)
            await callback.message.edit_text(
                "Выберите спот для чек-ина:", reply_markup=kb
            )
            await state.set_state(State("CheckinStates:selecting_spot"))
        else:
            await callback.message.edit_text(
                "Геолокация не найдена. Отправьте геолокацию заново."
            )
            await geo_service.request_location(callback.message, state, user_id)
            await state.set_state(State("CheckinStates:requesting_location"))
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "main_menu")
    async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
        """Обработка возврата в главное меню."""
        user_id = callback.from_user.id
        logger.info(f"Нажата кнопка 'В главное меню' от пользователя {user_id}")
        await state.clear()
        kb = MainKeyboards.get_main_menu()
        await callback.message.edit_text(
            "Добро пожаловать в WindSpotBot! 🏄‍♂️\n"
            "Найдите споты для виндсёрфинга, отметьтесь или подпишитесь на уведомления!",
            reply_markup=kb,
        )
        await callback.answer()
