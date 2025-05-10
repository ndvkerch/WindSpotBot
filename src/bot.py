import asyncio
import logging
import traceback
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from src.config.config import settings
from src.services.geo import GeoService
from src.services.topic import TopicService
from src.services.notification import NotificationService
from src.services.chat import ChatService
from src.services.spot import SpotService
from src.services.checkin import CheckinService
from src.services.weather import WeatherService
from src.repositories.subscription import SubscriptionRepository
from src.repositories.spot import SpotRepository
from src.repositories.checkin import CheckinRepository
from src.models.user import User
from src.keyboards.main import MainKeyboards
import aiosqlite

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CheckinStates(StatesGroup):
    """Состояния для процесса чек-ина."""

    requesting_location = State()
    selecting_spot = State()
    selecting_type = State()


class AddSpotStates(StatesGroup):
    """Состояния для добавления спота."""

    entering_name = State()
    entering_location = State()
    entering_description = State()


class SpotsStates(StatesGroup):
    """Состояния для просмотра спотов."""

    requesting_location = State()


class ActivityStates(StatesGroup):
    """Состояния для просмотра активности."""

    requesting_location = State()


async def main():
    """Инициализация и запуск бота."""
    logger.info("Инициализация модуля bot.py")
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    # Регистрация команд для меню Telegram
    await bot.set_my_commands(
        [
            BotCommand(command="/start", description="Запустить бота"),
            BotCommand(command="/checkin", description="Чек-ин на споте"),
            BotCommand(command="/spots", description="Посмотреть ближайшие споты"),
            BotCommand(command="/activity", description="Активность на спотах"),
            BotCommand(command="/add_spot", description="Добавить новый спот"),
            BotCommand(command="/subscribe", description="Подписаться на уведомления"),
            BotCommand(command="/create_topic", description="Создать тему для спота"),
            BotCommand(command="/test_notification", description="Тест уведомления"),
            BotCommand(command="/test_chat", description="Тест сообщения в чат"),
        ]
    )

    # Инициализация БД и сервисов
    async with aiosqlite.connect("data/database.db") as db:
        subscription_repo = SubscriptionRepository(db)
        spot_repo = SpotRepository(db)
        checkin_repo = CheckinRepository(db)
        geo_service = GeoService(bot)
        topic_service = TopicService(bot, db)
        notification_service = NotificationService(
            bot, topic_service, subscription_repo
        )
        chat_service = ChatService(bot, topic_service, notification_service)
        spot_service = SpotService(spot_repo, geo_service)
        weather_service = WeatherService()
        checkin_service = CheckinService(
            bot, checkin_repo, notification_service, spot_service
        )

        # Глобальный обработчик ошибок
        @dp.error()
        async def error_handler(event, **kwargs):
            """Обработка ошибок."""
            exception = kwargs.get("exception")
            if exception:
                logger.error(
                    f"Ошибка при обработке обновления: {exception}\n{traceback.format_exc()}"
                )
            else:
                logger.error(
                    f"Неизвестная ошибка при обработке обновления\n{traceback.format_exc()}"
                )
            return True

        # Хендлер для /start
        @dp.message(Command(commands=["start"]))
        async def cmd_start(message: Message, state: FSMContext):
            """Обработка команды /start."""
            user_id = message.from_user.id
            logger.info(f"Команда /start от пользователя {user_id}")
            await state.clear()
            kb = MainKeyboards.get_main_menu()
            await message.answer(
                "Добро пожаловать в WindSpotBot! 🏄‍♂️\n"
                "Найдите споты для виндсёрфинга, отметьтесь или подпишитесь на уведомления!",
                reply_markup=kb,
            )

        # Хендлер для чек-ина
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
                await state.set_state(CheckinStates.selecting_spot)
            else:
                await geo_service.request_location(message, state)
                await state.set_state(CheckinStates.requesting_location)

        # Обработка геолокации для чек-ина
        @dp.message(CheckinStates.requesting_location)
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
                await state.set_state(CheckinStates.selecting_spot)
            else:
                logger.error("Не удалось обработать геолокацию")
                await message.answer("Ошибка при обработке геолокации.")

        # Выбор спота для чек-ина
        @dp.callback_query(
            lambda c: c.data and c.data.startswith("spot:"),
            CheckinStates.selecting_spot,
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
                await state.set_state(CheckinStates.selecting_type)
                await callback.answer()
            except Exception as e:
                logger.error(f"Ошибка в callback_spot: {e}")
                await callback.message.edit_text(f"Ошибка при выборе спота: {str(e)}")

        # Выбор типа чек-ина
        @dp.callback_query(
            lambda c: c.data and c.data.startswith("checkin:"),
            CheckinStates.selecting_type,
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

        # Обработка кнопки "Назад" к запросу геолокации
        @dp.callback_query(lambda c: c.data == "back_to_location")
        async def callback_back_to_location(callback: CallbackQuery, state: FSMContext):
            """Обработка возврата к запросу геолокации."""
            user_id = callback.from_user.id
            logger.info(f"Нажата кнопка 'Назад' от пользователя {user_id}")
            await state.clear()
            await geo_service.request_location(callback.message, state)
            await state.set_state(CheckinStates.requesting_location)
            await callback.message.edit_text("Пожалуйста, отправьте геолокацию.")
            await callback.answer()

        # Обработка кнопки "Назад" к выбору спота
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
                await state.set_state(CheckinStates.selecting_spot)
            else:
                await callback.message.edit_text(
                    "Геолокация не найдена. Отправьте геолокацию заново."
                )
                await state.set_state(CheckinStates.requesting_location)
            await callback.answer()

        # Обработка кнопки "В главное меню"
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

        # Хендлер для просмотра активности
        @dp.message(Command(commands=["activity"]))
        async def cmd_activity(
            message: Message, state: FSMContext, user_id: int = None
        ):
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
                )
            else:
                await geo_service.request_location(message, state)
                await state.set_state(ActivityStates.requesting_location)

        # Обработка геолокации для активности
        @dp.message(ActivityStates.requesting_location)
        async def process_activity_location(message: Message, state: FSMContext):
            """Обработка геолокации для активности."""
            user_id = message.from_user.id
            logger.info(
                f"Обработка геолокации для активности от пользователя {user_id}"
            )
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
                )
                await state.clear()
            else:
                logger.error("Не удалось обработать геолокацию")
                await message.answer("Ошибка при обработке геолокации.")

        async def show_activity(
            message: Message,
            latitude: float,
            longitude: float,
            spot_service: SpotService,
            checkin_service: CheckinService,
            weather_service: WeatherService,
            chat_service: ChatService,
            user_id: int,
        ):
            """Отображение активности на спотах."""
            logger.info(f"Отображение активности для пользователя {user_id}")
            spots = await spot_service.get_all_spots()
            nearby_spots = await geo_service.get_nearby_spots(
                spots, latitude, longitude
            )
            if not nearby_spots:
                await message.answer("Активные споты не найдены.")
                return
            # Фильтрация спотов с активными чек-инами (типы 1 и 3)
            active_spots = []
            for spot_with_distance in nearby_spots[:10]:
                spot = spot_with_distance.spot
                on_spot, planning = await checkin_service.get_active_users(spot.id)
                if on_spot or planning:
                    active_spots.append(spot_with_distance)
            if not active_spots:
                await message.answer("Нет спотов с активностью поблизости.")
                return
            # Сохранение message_id для каждого спота
            message_ids = []
            for spot_with_distance in active_spots:
                spot = spot_with_distance.spot
                weather = await weather_service.get_weather(
                    spot.latitude, spot.longitude
                )
                logger.info(
                    f"Получены погодные данные для спота {spot.name}: {weather}"
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
                chat_link = await chat_service.get_chat_link(spot.name)
                chat_info = f"💬 Чат: {chat_link}" if chat_link else "💬 Чат: не создан"
                response = (
                    f"📍 {spot.name} ({spot_with_distance.distance:.1f} км)\n"
                    f"{weather_info}\n"
                    f"{on_spot_info}\n"
                    f"{planning_info}\n"
                    f"{chat_info}"
                )
                sent_message = await message.answer(response)
                message_ids.append((spot.id, sent_message.message_id))
            # Сохранение message_ids в состоянии
            await state.update_data(activity_message_ids=message_ids)
            # Добавление кнопок управления
            kb = MainKeyboards.get_activity_controls()
            await message.answer("Управление активностью:", reply_markup=kb)

        # Хендлер для кнопки "Обновить всё"
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
                    await callback.message.edit_text(
                        "Нет спотов с активностью поблизости."
                    )
                    return
                new_message_ids = []
                for spot_with_distance in active_spots:
                    spot = spot_with_distance.spot
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
                    chat_link = await chat_service.get_chat_link(spot.name)
                    chat_info = (
                        f"💬 Чат: {chat_link}" if chat_link else "💬 Чат: не создан"
                    )
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
                                new_message_ids.append((spot.id, message_id))
                            else:
                                logger.error(
                                    f"Ошибка при обновлении сообщения для спота {spot.id}: {e}"
                                )
                    else:
                        sent_message = await callback.message.answer(response)
                        new_message_ids.append((spot.id, sent_message.message_id))
                await state.update_data(activity_message_ids=new_message_ids)
                kb = MainKeyboards.get_activity_controls()
                await callback.message.edit_text(
                    "Управление активностью:", reply_markup=kb
                )
                await callback.answer()
            except Exception as e:
                logger.error(f"Ошибка в callback_refresh_all: {e}")
                await callback.message.edit_text(
                    f"Ошибка при обновлении спотов: {str(e)}"
                )
                await callback.answer()

        # Хендлер для кнопки "Обновить геопозицию"
        @dp.callback_query(lambda c: c.data == "refresh_location")
        async def callback_refresh_location(callback: CallbackQuery, state: FSMContext):
            """Обработка нажатия на кнопку 'Обновить геопозицию'."""
            user_id = callback.from_user.id
            logger.info(f"Обработка refresh_location от пользователя {user_id}")
            await state.clear()
            await geo_service.request_location(callback.message, state)
            await state.set_state(ActivityStates.requesting_location)
            await callback.message.edit_text("Пожалуйста, отправьте новую геолокацию.")
            await callback.answer()

        # Хендлер для списка спотов
        @dp.message(Command(commands=["spots"]))
        async def cmd_spots(message: Message, state: FSMContext, user_id: int = None):
            """Обработка команды /spots."""
            user_id = user_id or message.from_user.id
            logger.info(f"Команда /spots от пользователя {user_id}")
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
                await message.answer("Ближайшие споты:", reply_markup=kb)
            else:
                await geo_service.request_location(message, state)
                await state.set_state(SpotsStates.requesting_location)

        # Обработка геолокации для спотов
        @dp.message(SpotsStates.requesting_location)
        async def process_spots_location(message: Message, state: FSMContext):
            """Обработка геолокации и отображение ближайших спотов."""
            user_id = message.from_user.id
            logger.info(f"Обработка геолокации для спотов от пользователя {user_id}")
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
                await message.answer("Ближайшие споты:", reply_markup=kb)
                await state.clear()
            else:
                logger.error("Не удалось обработать геолокацию")
                await message.answer("Ошибка при обработке геолокации.")

        # Хендлер для добавления спота
        @dp.message(Command(commands=["add_spot"]))
        async def cmd_add_spot(message: Message, state: FSMContext):
            """Начало процесса добавления спота."""
            user_id = message.from_user.id
            logger.info(f"Команда /add_spot от пользователя {user_id}")
            await state.clear()
            await message.answer("Введите название спота:")
            await state.set_state(AddSpotStates.entering_name)

        @dp.message(AddSpotStates.entering_name)
        async def process_spot_name(message: Message, state: FSMContext):
            """Обработка названия спота."""
            user_id = message.from_user.id
            logger.info(f"Обработка названия спота от пользователя {user_id}")
            name = message.text.strip()
            if not name:
                await message.answer("Название не может быть пустым. Попробуйте снова:")
                return
            await state.update_data(name=name)
            await message.answer(
                "Отправьте геолокацию спота (используйте кнопку 'Отправить геолокацию' в Telegram):"
            )
            await state.set_state(AddSpotStates.entering_location)

        @dp.message(AddSpotStates.entering_location)
        async def process_spot_location(message: Message, state: FSMContext):
            """Обработка геолокации спота."""
            user_id = message.from_user.id
            logger.info(f"Обработка геолокации спота от пользователя {user_id}")
            if message.content_type not in ["location", "venue"]:
                logger.warning(f"Получен неверный тип контента: {message.content_type}")
                await message.answer("Пожалуйста, отправьте геолокацию или место.")
                return
            if message.content_type == "location":
                latitude = message.location.latitude
                longitude = message.location.longitude
            else:
                latitude = message.venue.location.latitude
                longitude = message.venue.location.longitude
            logger.info(f"Получена геолокация спота: ({latitude}, {longitude})")
            await state.update_data(latitude=latitude, longitude=longitude)
            await message.answer(
                "Введите описание спота (или отправьте /skip, чтобы пропустить):"
            )
            await state.set_state(AddSpotStates.entering_description)

        @dp.message(AddSpotStates.entering_description)
        async def process_spot_description(message: Message, state: FSMContext):
            """Обработка описания спота."""
            user_id = message.from_user.id
            logger.info(f"Обработка описания спота от пользователя {user_id}")
            data = await state.get_data()
            description = None if message.text == "/skip" else message.text.strip()
            try:
                spot_id = await spot_service.add_spot(
                    name=data["name"],
                    latitude=data["latitude"],
                    longitude=data["longitude"],
                    created_by=user_id,
                    description=description,
                )
                if spot_id:
                    await message.answer(f"Спот '{data['name']}' успешно добавлен!")
                else:
                    await message.answer("Ошибка при добавлении спота.")
                await state.clear()
            except Exception as e:
                logger.error(f"Ошибка при добавлении спота: {e}")
                await message.answer(f"Ошибка: {str(e)}")
                await state.clear()

        # Хендлер для создания темы
        @dp.message(Command(commands=["create_topic"]))
        async def cmd_create_topic(message: Message):
            """Создание темы для спота."""
            user_id = message.from_user.id
            logger.info(f"Команда /create_topic от пользователя {user_id}")
            try:
                chat_member = await bot.get_chat_member(settings.CHAT_ID, bot.id)
                if not chat_member.can_manage_topics:
                    await message.answer(
                        "Бот не имеет прав для создания тем. Дайте права администратора с 'Управление темами'."
                    )
                    return
                spot_name = (
                    message.text.split(maxsplit=1)[1]
                    if len(message.text.split()) > 1
                    else "Тест"
                )
                thread_id = await topic_service.create_topic(spot_name)
                if thread_id:
                    await message.answer(
                        f"Тема '{spot_name}' создана, thread_id: {thread_id}"
                    )
                else:
                    await message.answer(f"Ошибка при создании темы '{spot_name}'")
            except Exception as e:
                logger.error(f"Ошибка в cmd_create_topic: {e}")
                await message.answer(f"Не удалось создать тему: {e}")

        # Хендлер для подписки
        @dp.message(Command(commands=["subscribe"]))
        async def cmd_subscribe(message: Message):
            """Подписка на события спота."""
            user_id = message.from_user.id
            logger.info(f"Команда /subscribe от пользователя {user_id}")
            try:
                parts = message.text.split(maxsplit=1)
                if len(parts) < 2:
                    await message.answer(
                        "Использование: /subscribe <spot_name> <event_type>"
                    )
                    return
                command_args = parts[1].rsplit(maxsplit=1)
                if len(command_args) < 2:
                    await message.answer(
                        "Укажите название спота и тип события (checkin, message, weather)"
                    )
                    return
                spot_name, event_type = command_args
                if event_type not in ["checkin", "message", "weather"]:
                    await message.answer(
                        "Неверный тип события. Допустимые значения: checkin, message, weather"
                    )
                    return
                await subscription_repo.create(user_id, spot_name, event_type)
                await message.answer(
                    f"Подписка на '{spot_name}' ({event_type}) создана"
                )
            except Exception as e:
                logger.error(f"Ошибка в cmd_subscribe: {e}")
                await message.answer(f"Не удалось создать подписку: {e}")

        # Хендлер для теста уведомлений
        @dp.message(Command(commands=["test_notification"]))
        async def cmd_test_notification(message: Message):
            """Тест отправки уведомления."""
            user_id = message.from_user.id
            logger.info(f"Команда /test_notification от пользователя {user_id}")
            try:
                parts = message.text.split(maxsplit=2)
                if len(parts) < 3:
                    await message.answer(
                        "Использование: /test_notification <spot_name> <event_type>"
                    )
                    return
                spot_name, event_type = parts[1], parts[2]
                user = User(
                    id=user_id,
                    name=message.from_user.full_name,
                    username=message.from_user.username,
                )
                if event_type == "checkin":
                    await notification_service.send_checkin_notification(
                        user, spot_name
                    )
                elif event_type == "message":
                    await notification_service.send_message_notification(
                        spot_name, "Тестовое сообщение", user
                    )
                elif event_type == "weather":
                    await notification_service.send_weather_notification(
                        spot_name, {"wind_speed": 7.5}
                    )
                await message.answer(
                    f"Уведомление для '{spot_name}' ({event_type}) отправлено"
                )
            except Exception as e:
                logger.error(f"Ошибка в cmd_test_notification: {e}")
                await message.answer(f"Не удалось отправить уведомление: {e}")

        # Хендлер для теста чата
        @dp.message(Command(commands=["test_chat"]))
        async def cmd_test_chat(message: Message):
            """Тест отправки сообщения в тему."""
            user_id = message.from_user.id
            logger.info(f"Команда /test_chat от пользователя {user_id}")
            try:
                spot_name = (
                    message.text.split(maxsplit=1)[1]
                    if len(message.text.split()) > 1
                    else "Тест"
                )
                message_id = await chat_service.send_message_to_spot(
                    spot_name, "Тестовое сообщение", user_id
                )
                if message_id:
                    await message.answer(
                        f"Сообщение отправлено в тему '{spot_name}', message_id: {message_id}"
                    )
                else:
                    await message.answer(f"Ошибка при отправке в тему '{spot_name}'")
            except Exception as e:
                logger.error(f"Ошибка в cmd_test_chat: {e}")
                await message.answer(f"Не удалось отправить сообщение: {e}")

        # Хендлер для кнопок главного меню
        @dp.callback_query(
            lambda c: c.data in ["checkin", "spots", "activity", "add_spot"]
        )
        async def process_main_menu(callback: CallbackQuery, state: FSMContext):
            """Обработка нажатий на кнопки главного меню."""
            user_id = callback.from_user.id
            logger.info(
                f"Обработка callback главного меню: {callback.data} от пользователя {user_id}"
            )
            try:
                if callback.data == "checkin":
                    await cmd_checkin(callback.message, state, user_id=user_id)
                elif callback.data == "spots":
                    await cmd_spots(callback.message, state, user_id=user_id)
                elif callback.data == "activity":
                    await cmd_activity(callback.message, state, user_id=user_id)
                elif callback.data == "add_spot":
                    await cmd_add_spot(callback.message, state)
                await callback.answer()
            except Exception as e:
                logger.error(
                    f"Ошибка в process_main_menu: {e}\n{traceback.format_exc()}"
                )
                await callback.message.answer(f"Ошибка: {str(e)}")

        # Запуск бота
        logger.info("Бот запущен")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
