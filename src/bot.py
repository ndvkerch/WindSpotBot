import asyncio
import logging
import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
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

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Инициализация модуля bot.py")


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
    """Запуск бота."""
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Инициализация БД
    async with aiosqlite.connect("data/database.db") as db:
        # Инициализация сервисов
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

        # Хендлер для /start
        @dp.message(Command(commands=["start"]))
        async def cmd_start(message: Message):
            """Обработка команды /start."""
            logger.info(f"Команда /start от пользователя {message.from_user.id}")
            kb = MainKeyboards.get_main_menu()
            await message.answer(
                "Добро пожаловать в WindSpotBot! 🏄‍♂️\n"
                "Найдите споты для виндсёрфинга, отметьтесь или подпишитесь на уведомления!",
                reply_markup=kb,
            )

        # Хендлер для чек-ина
        @dp.message(Command(commands=["checkin"]))
        async def cmd_checkin(message: Message, state: FSMContext):
            """Начало процесса чек-ина."""
            logger.info(f"Команда /checkin от пользователя {message.from_user.id}")
            try:
                user_id = message.from_user.id
                location = await geo_service.get_cached_location(user_id)
                if location:
                    logger.info(
                        f"Используется кэшированная геолокация для пользователя {user_id}: {location}"
                    )
                    latitude, longitude = location
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
                    await message.answer("Выберите спот для чек-ина:", reply_markup=kb)
                    await state.set_state(CheckinStates.selecting_spot)
                else:
                    await geo_service.request_location(message, state)
                    await state.set_state(CheckinStates.requesting_location)
            except Exception as e:
                logger.error(f"Ошибка в cmd_checkin: {e}")
                await message.answer(f"Ошибка: {str(e)}")

        # Обработка геолокации для чек-ина
        @dp.message(CheckinStates.requesting_location)
        async def process_checkin_location(message: Message, state: FSMContext):
            """Обработка геолокации для чек-ина."""
            logger.info(
                f"Обработка геолокации для чек-ина от пользователя {message.from_user.id}"
            )
            if message.content_type not in ["location", "venue"]:
                logger.warning(f"Получен неверный тип контента: {message.content_type}")
                await message.answer("Пожалуйста, отправьте геолокацию или место.")
                return
            if message.content_type == "location":
                location = await geo_service.process_location(message, state)
            else:  # venue
                latitude = message.venue.location.latitude
                longitude = message.venue.location.longitude
                await geo_service.cache_location(
                    message.from_user.id, latitude, longitude
                )
                location = (latitude, longitude)
                await state.clear()
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
            logger.info(
                f"Выбор спота: {callback.data} пользователем {callback.from_user.id}"
            )
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
            logger.info(
                f"Выбор типа чек-ина: {callback.data} пользователем {callback.from_user.id}"
            )
            try:
                data = await state.get_data()
                spot_id = data.get("spot_id")
                if not spot_id:
                    await callback.message.edit_text("Ошибка: спот не выбран.")
                    return
                checkin_type = int(callback.data.split(":", 1)[1])
                user = User(
                    id=callback.from_user.id,
                    name=callback.from_user.full_name,
                    username=callback.from_user.username,
                )
                success = await checkin_service.create_checkin(
                    user, spot_id, checkin_type, duration=3600
                )
                spot = await spot_service.get_spot_by_id(spot_id)
                if success:
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

        # Хендлер для просмотра активности
        @dp.message(Command(commands=["activity"]))
        async def cmd_activity(message: Message, state: FSMContext):
            """Просмотр активности на ближайших спотах."""
            logger.info(f"Команда /activity от пользователя {message.from_user.id}")
            try:
                user_id = message.from_user.id
                location = await geo_service.get_cached_location(user_id)
                if location:
                    logger.info(
                        f"Используется кэшированная геолокация для пользователя {user_id}: {location}"
                    )
                    latitude, longitude = location
                    await show_activity(
                        message,
                        latitude,
                        longitude,
                        spot_service,
                        checkin_service,
                        weather_service,
                        chat_service,
                    )
                    await state.clear()
                else:
                    await geo_service.request_location(message, state)
                    await state.set_state(ActivityStates.requesting_location)
            except Exception as e:
                logger.error(f"Ошибка в cmd_activity: {e}")
                await message.answer(f"Ошибка: {str(e)}")

        # Обработка геолокации для активности
        @dp.message(ActivityStates.requesting_location)
        async def process_activity_location(message: Message, state: FSMContext):
            """Обработка геолокации для активности."""
            logger.info(
                f"Обработка геолокации для активности от пользователя {message.from_user.id}"
            )
            if message.content_type not in ["location", "venue"]:
                logger.warning(f"Получен неверный тип контента: {message.content_type}")
                await message.answer("Пожалуйста, отправьте геолокацию или место.")
                return
            if message.content_type == "location":
                location = await geo_service.process_location(message, state)
            else:  # venue
                latitude = message.venue.location.latitude
                longitude = message.venue.location.longitude
                await geo_service.cache_location(
                    message.from_user.id, latitude, longitude
                )
                location = (latitude, longitude)
                await state.clear()
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
                )
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
        ):
            """Отображение активности на спотах."""
            logger.info(
                f"Отображение активности для пользователя {message.from_user.id}"
            )
            spots = await spot_service.get_all_spots()
            nearby_spots = await geo_service.get_nearby_spots(
                spots, latitude, longitude
            )
            if not nearby_spots:
                await message.answer("Активные споты не найдены.")
                return
            response = "Активность на спотах:\n"
            for spot in nearby_spots:
                # Погода
                weather = await weather_service.get_weather(
                    spot.latitude, spot.longitude
                )
                weather_info = "Погода: нет данных"
                if weather:
                    weather_info = f"Ветер: {weather['wind_speed'] or 'N/A'} м/с, Вода: {weather['water_temperature'] or 'N/A'} °C"

                # Пользователи
                on_spot, planning = await checkin_service.get_active_users(spot.id)
                on_spot_info = (
                    f"На месте: {len(on_spot)} чел." if on_spot else "На месте: никого"
                )
                planning_info = (
                    f"Планируют: {len(planning)} чел."
                    if planning
                    else "Планируют: никого"
                )

                # Чат
                chat_link = await chat_service.get_chat_link(spot.name)
                chat_info = f"Чат: {chat_link}" if chat_link else "Чат: не создан"

                response += (
                    f"\n- {spot.name} ({spot.distance:.1f} км)\n"
                    f"  {weather_info}\n"
                    f"  {on_spot_info}\n"
                    f"  {planning_info}\n"
                    f"  {chat_info}\n"
                )
            await message.answer(response)

        # Хендлер для списка спотов
        @dp.message(Command(commands=["spots"]))
        async def cmd_spots(message: Message, state: FSMContext):
            """Запрос геолокации для отображения ближайших спотов."""
            logger.info(f"Команда /spots от пользователя {message.from_user.id}")
            try:
                user_id = message.from_user.id
                location = await geo_service.get_cached_location(user_id)
                if location:
                    logger.info(
                        f"Используется кэшированная геолокация для пользователя {user_id}: {location}"
                    )
                    latitude, longitude = location
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
                    await geo_service.request_location(message, state)
                    await state.set_state(SpotsStates.requesting_location)
            except Exception as e:
                logger.error(f"Ошибка в cmd_spots: {e}")
                await message.answer(f"Ошибка: {str(e)}")

        # Обработка геолокации для спотов
        @dp.message(SpotsStates.requesting_location)
        async def process_spots_location(message: Message, state: FSMContext):
            """Обработка геолокации и отображение ближайших спотов."""
            logger.info(
                f"Обработка геолокации для спотов от пользователя {message.from_user.id}"
            )
            if message.content_type not in ["location", "venue"]:
                logger.warning(f"Получен неверный тип контента: {message.content_type}")
                await message.answer("Пожалуйста, отправьте геолокацию или место.")
                return
            if message.content_type == "location":
                location = await geo_service.process_location(message, state)
            else:  # venue
                latitude = message.venue.location.latitude
                longitude = message.venue.location.longitude
                await geo_service.cache_location(
                    message.from_user.id, latitude, longitude
                )
                location = (latitude, longitude)
                await state.clear()
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
            else:
                logger.error("Не удалось обработать геолокацию")
                await message.answer("Ошибка при обработке геолокации.")

        # Хендлер для /add_spot
        @dp.message(Command(commands=["add_spot"]))
        async def cmd_add_spot(message: Message, state: FSMContext):
            """Начало процесса добавления спота."""
            logger.info(f"Команда /add_spot от пользователя {message.from_user.id}")
            await message.answer("Введите название спота:")
            await state.set_state(AddSpotStates.entering_name)

        @dp.message(AddSpotStates.entering_name)
        async def process_spot_name(message: Message, state: FSMContext):
            """Обработка названия спота."""
            logger.info(
                f"Обработка названия спота от пользователя {message.from_user.id}"
            )
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
            logger.info(
                f"Обработка геолокации спота от пользователя {message.from_user.id}"
            )
            if message.content_type not in ["location", "venue"]:
                logger.warning(f"Получен неверный тип контента: {message.content_type}")
                await message.answer("Пожалуйста, отправьте геолокацию или место.")
                return
            if message.content_type == "location":
                latitude = message.location.latitude
                longitude = message.location.longitude
            else:  # venue
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
            logger.info(
                f"Обработка описания спота от пользователя {message.from_user.id}"
            )
            data = await state.get_data()
            description = None if message.text == "/skip" else message.text.strip()
            try:
                spot_id, error = await spot_service.add_spot(
                    name=data["name"],
                    latitude=data["latitude"],
                    longitude=data["longitude"],
                    created_by=message.from_user.id,
                    description=description,
                )
                if spot_id:
                    await message.answer(f"Спот '{data['name']}' успешно добавлен!")
                else:
                    await message.answer(f"Ошибка: {error}")
                await state.clear()
            except Exception as e:
                logger.error(f"Ошибка при добавлении спота: {e}")
                await message.answer(f"Ошибка: {str(e)}")
                await state.clear()

        # Хендлер для создания темы
        @dp.message(Command(commands=["create_topic"]))
        async def cmd_create_topic(message: Message):
            """Создание темы для спота."""
            logger.info(f"Команда /create_topic от пользователя {message.from_user.id}")
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
                    await message.answer(f"Ошибка при создания темы '{spot_name}'")
            except Exception as e:
                logger.error(f"Ошибка в cmd_create_topic: {e}")
                await message.answer(f"Не удалось создать тему: {e}")

        # Хендлер для подписки
        @dp.message(Command(commands=["subscribe"]))
        async def cmd_subscribe(message: Message):
            """Тестовая подписка на события."""
            logger.info(f"Команда /subscribe от пользователя {message.from_user.id}")
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
                spot_name, event_type = command_args[0], command_args[1]
                logger.info(
                    f"Обработка подписки: spot_name='{spot_name}', event_type='{event_type}'"
                )
                if event_type not in ["checkin", "message", "weather"]:
                    await message.answer(
                        "Неверный тип события. Допустимые значения: checkin, message, weather"
                    )
                    return
                await subscription_repo.create(
                    message.from_user.id, spot_name, event_type
                )
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
            logger.info(
                f"Команда /test_notification от пользователя {message.from_user.id}"
            )
            try:
                parts = message.text.split(maxsplit=2)
                if len(parts) < 3:
                    await message.answer(
                        "Использование: /test_notification <spot_name> <event_type>"
                    )
                    return
                spot_name, event_type = parts[1], parts[2]
                user = User(
                    id=message.from_user.id,
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
            logger.info(f"Команда /test_chat от пользователя {message.from_user.id}")
            try:
                spot_name = (
                    message.text.split(maxsplit=1)[1]
                    if len(message.text.split()) > 1
                    else "Тест"
                )
                message_id = await chat_service.send_message_to_spot(
                    spot_name, "Тестовое сообщение", message.from_user.id
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
            logger.info(
                f"Обработка callback главного меню: {callback.data} от пользователя {callback.from_user.id}"
            )
            try:
                if callback.data == "checkin":
                    await cmd_checkin(callback.message, state)
                elif callback.data == "spots":
                    await cmd_spots(callback.message, state)
                elif callback.data == "activity":
                    await cmd_activity(callback.message, state)
                elif callback.data == "add_spot":
                    await cmd_add_spot(callback.message, state)
                await callback.answer()
            except Exception as e:
                logger.error(f"Ошибка в process_main_menu: {e}")
                await callback.message.answer(f"Ошибка: {str(e)}")

        # Временный хендлер для отладки всех сообщений
        @dp.message()
        async def debug_location(message: Message, state: FSMContext):
            """Отладка всех входящих сообщений."""
            current_state = await state.get_state()
            logger.info(
                f"Получено сообщение от {message.from_user.id}, content_type: {message.content_type}, state: {current_state}"
            )
            if message.content_type in ["location", "venue"]:
                latitude = (
                    message.location.latitude
                    if message.content_type == "location"
                    else message.venue.location.latitude
                )
                longitude = (
                    message.location.longitude
                    if message.content_type == "location"
                    else message.venue.location.longitude
                )
                logger.info(f"Геолокация: ({latitude}, {longitude})")
                await message.answer(
                    f"Получена геолокация: ({latitude}, {longitude}), состояние: {current_state}"
                )

        logger.info("Бот запущен")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
