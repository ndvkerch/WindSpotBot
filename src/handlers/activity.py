import logging
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from src.bot import show_activity
from src.services.geo import GeoService
from src.services.spot import SpotService
from src.services.checkin import CheckinService
from src.services.weather import WeatherService
from src.services.chat import ChatService
from src.keyboards.main import MainKeyboards

logger = logging.getLogger(__name__)


def register_activity_handlers(
    dp: Dispatcher,
    geo_service: GeoService,
    spot_service: SpotService,
    checkin_service: CheckinService,
    weather_service: WeatherService,
    chat_service: ChatService,
):
    """Регистрация хендлеров для команды /activity."""

    @dp.message(Command(commands=["activity"]))
    async def cmd_activity(message: Message, state: FSMContext, user_id: int = None):
        """Обработка команды /activity."""
        user_id = user_id or message.from_user.id
        logger.info(f"Команда /activity от пользователя {user_id}")
        await state.clear()
        cached_location = await geo_service.get_cached_location(user_id)
        if cached_location:
            latitude, longitude = cached_location
            logger.info(f"Использован кэш: ({latitude}, {longitude})")
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
            )
        else:
            await geo_service.request_location(message, state, user_id)
            await state.set_state(State("ActivityStates:requesting_location"))

    @dp.message(State("ActivityStates:requesting_location"))
    async def process_activity_location(message: Message, state: FSMContext):
        """Обработка геолокации для активности."""
        user_id = message.from_user.id
        logger.info(f"Обработка геолокации для активности от пользователя {user_id}")
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
            )
            await state.clear()
        else:
            logger.error("Не удалось обработать геолокацию")
            await message.answer("Ошибка при обработке геолокации.")

    @dp.callback_query(lambda c: c.data == "refresh_all")
    async def callback_refresh_all(callback: CallbackQuery, state: FSMContext):
        """Обработка нажатия на кнопку 'Обновить всё'."""
        user_id = callback.from_user.id
        logger.info(f"Обработка refresh_all от пользователя {user_id}")
        try:
            cached_location = await geo_service.get_cached_location(user_id)
            if not cached_location:
                await callback.message.edit_text(
                    "Геолокация не найдена. Отправьте геолокацию через /activity."
                )
                return
            latitude, longitude = cached_location
            state_data = await state.get_data()
            message_ids = state_data.get("activity_message_ids", [])
            if not message_ids:
                await callback.message.edit_text(
                    "Нет данных для обновления. Выполните /activity заново."
                )
                return
            spots = await spot_service.get_all_spots()
            nearby_spots = await geo_service.get_nearby_spots(
                spots, latitude, longitude
            )
            active_spots = []
            for spot_with_distance in nearby_spots[:10]:
                spot = spot_with_distance.spot
                on_spot, planning = await checkin_service.get_active_users(spot.id)
                if on_spot or planning:
                    active_spots.append(spot_with_distance)
            if not active_spots:
                await callback.message.edit_text("Нет спотов с активностью поблизости.")
                return
            new_message_ids = []
            for spot_with_distance in active_spots:
                spot = spot_with_distance.spot
                try:
                    weather = await weather_service.get_weather(
                        spot.latitude, spot.longitude, force_refresh=True
                    )
                    logger.info(
                        f"Получены обновлённые погодные данные для спота {spot.name}: {weather}"
                    )
                    weather_info = "🌫 Погода: нет данных"
                    if weather:
                        wind_speed = weather.get("wind_speed", "N/A")
                        wind_direction = weather_service.wind_direction_to_text(
                            weather.get("wind_direction", None)
                        )
                        wind_gusts = weather.get("wind_gusts", "N/A")
                        water_temp = weather.get("water_temperature", "N/A")
                        weather_info = (
                            f"🌬 Ветер: {wind_speed} м/с\n"
                            f"🧭 Направление: {wind_direction}\n"
                            f"💨 Порывы: {wind_gusts} м/с\n"
                            f"🌊 Вода: {water_temp} °C"
                        )
                except Exception as e:
                    logger.error(
                        f"Ошибка при получении погоды для спота {spot.name}: {e}"
                    )
                    weather_info = "🌫 Погода: ошибка"
                on_spot, planning = await checkin_service.get_active_users(spot.id)
                on_spot_info = (
                    f"🏄 На месте: {len(on_spot)} чел."
                    if on_spot
                    else "🏄 На месте: никого"
                )
                planning_info = (
                    f"⏳ Планируют: {len(planning)} чел."
                    if planning
                    else "⏳ Планируют: никого"
                )
                try:
                    chat_link = await chat_service.get_chat_link(spot.name)
                    chat_info = (
                        f"💬 Чат: {chat_link}" if chat_link else "💬 Чат: не создан"
                    )
                except Exception as e:
                    logger.error(
                        f"Ошибка при получении ссылки на чат для спота {spot.name}: {e}"
                    )
                    chat_info = "💬 Чат: ошибка"
                response = (
                    f"📍 {spot.name} ({spot_with_distance.distance:.1f} км)\n"
                    f"{weather_info}\n"
                    f"{on_spot_info}\n"
                    f"{planning_info}\n"
                    f"{chat_info}"
                )
                message_id = next(
                    (mid for sid, mid in message_ids if sid == spot.id), None
                )
                if message_id:
                    try:
                        await callback.message.bot.edit_message_text(
                            text=response,
                            chat_id=callback.message.chat.id,
                            message_id=message_id,
                        )
                        new_message_ids.append((spot.id, message_id))
                    except Exception as e:
                        if "message is not modified" in str(e):
                            logger.debug(
                                f"Сообщение для спота {spot.id} не изменилось, пропуск обновления"
                            )
                            new_message_ids.append((spot.id, message_id))
                        else:
                            logger.error(
                                f"Ошибка при обновлении сообщения для спота {spot.id}: {e}"
                            )
                            sent_message = await callback.message.answer(response)
                            new_message_ids.append((spot.id, sent_message.message_id))
                else:
                    sent_message = await callback.message.answer(response)
                    new_message_ids.append((spot.id, sent_message.message_id))
            await state.update_data(activity_message_ids=new_message_ids)
            kb = MainKeyboards.get_activity_controls()
            try:
                await callback.message.edit_text(
                    "Управление активностью:", reply_markup=kb
                )
            except Exception as e:
                if "message is not modified" in str(e):
                    logger.debug(
                        "Клавиатура управления активностью не изменилась, пропуск обновления"
                    )
                else:
                    logger.error(f"Ошибка при обновлении клавиатуры управления: {e}")
                    await callback.message.answer(
                        "Управление активностью:", reply_markup=kb
                    )
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_refresh_all: {e}")
            await callback.message.edit_text(f"Ошибка при обновлении спотов: {str(e)}")
            await callback.answer()

    @dp.callback_query(lambda c: c.data == "refresh_location")
    async def callback_refresh_location(callback: CallbackQuery, state: FSMContext):
        """Обработка нажатия на кнопку 'Обновить геопозицию'."""
        user_id = callback.from_user.id
        logger.info(f"Обработка refresh_location от пользователя {user_id}")
        await state.clear()
        await geo_service.request_location(callback.message, state, user_id)
        await state.set_state(State("ActivityStates:requesting_location"))
        await callback.message.edit_text("Пожалуйста, отправьте новую геолокацию.")
        await callback.answer()
