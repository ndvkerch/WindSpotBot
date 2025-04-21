import asyncio
import logging
import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, ContentTypeFilter
from aiogram.types import Message, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.config.config import settings
from src.services.geo import GeoService, GeoStates
from src.services.topic import TopicService
from src.services.notification import NotificationService
from src.services.chat import ChatService
from src.services.spot import SpotService
from src.services.checkin import CheckinService
from src.repositories.subscription import SubscriptionRepository
from src.repositories.spot import SpotRepository
from src.repositories.checkin import CheckinRepository
from src.models.user import User
from src.keyboards.main import MainKeyboards

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CheckinStates(StatesGroup):
    """Состояния для процесса чек-ина."""

    selecting_spot = State()
    selecting_type = State()


class AddSpotStates(StatesGroup):
    """Состояния для добавления спота."""

    entering_name = State()
    entering_location = State()
    entering_description = State()


class ActivityStates(StatesGroup):
    """Состояния для просмотра активности."""

    viewing_activity = State()


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
        checkin_service = CheckinService(
            bot, checkin_repo, notification_service, spot_service
        )

        # Хендлер для /start
        @dp.message(Command(commands=["start"]))
        async def cmd_start(message: Message):
            """Обработка команды /start."""
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
            try:
                user_id = message.from_user.id
                location = await geo_service.get_cached_location(user_id)
                if location:
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
            except Exception as e:
                logger.error(f"Ошибка в cmd_checkin: {e}")
                await message.answer(f"Ошибка: {str(e)}")

        # Обработка геолокации для чек-ина
        @dp.message(
            GeoStates.requesting_location,
            ContentTypeFilter(content_types=ContentType.LOCATION),
        )
        async def process_checkin_location(message: Message, state: FSMContext):
            """Обработка геолокации для чек-ина."""
            location = await geo_service.process_location(message, state)
            if location:
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

        # Выбор спота для чек-ина
        @dp.message(
            lambda c: c.data and c.data.startswith("spot:"),
            CheckinStates.selecting_spot,
        )
        async def callback_spot(callback: types.CallbackQuery, state: FSMContext):
            """Обработка выбора спота."""
            try:
                spot_name = callback.data.split(":", 1)[1]
                spot = await spot_service.get_spot(spot_name)
                if not spot:
                    await callback.message.edit_text(f"Спот '{spot_name}' не найден.")
                    return
                kb = MainKeyboards.get_checkin_types()
                await callback.message.edit_text(
                    f"Вы выбрали спот '{spot_name}'. Тип чек-ина:", reply_markup=kb
                )
                await state.update_data(spot_id=spot.id)
                await state.set_state(CheckinStates.selecting_type)
                await callback.answer()
            except Exception as e:
                logger.error(f"Ошибка в callback_spot: {e}")
                await callback.message.edit_text(f"Ошибка при выборе спота: {str(e)}")

        # Выбор типа чек-ина
        @dp.message(
            lambda c: c.data and c.data.startswith("checkin:"),
            CheckinStates.selecting_type,
        )
        async def callback_checkin(callback: types.CallbackQuery, state: FSMContext):
            """Обработка чек-ина."""
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
            try:
                user_id = message.from_user.id
                location = await geo_service.get_cached_location(user_id)
                if location:
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
            except Exception as e:
                logger.error(f"Ошибка в cmd_activity: {e}")
                await message.answer(f"Ошибка: {str(e)}")

        # Обработка геолокации для активности
        @dp.message(
            GeoStates.requesting_location,
            ContentTypeFilter(content_types=ContentType.LOCATION),
        )
        async def process_activity_location(message: Message, state: FSMContext):
            """Обработка геолокации для активности."""
            location = await geo_service.process_location(message, state)
            if location:
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
            try:
                user_id = message.from_user.id
                location = await geo_service.get_cached_location(user_id)
                if location:
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
            except Exception as e:
                logger.error(f"Ошибка в cmd_spots: {e}")
                await message.answer(f"Ошибка: {str(e)}")

        # Обработка геолокации для спотов
        @dp.message(
            GeoStates.requesting_location,
            ContentTypeFilter(content_types=ContentType.LOCATION),
        )
        async def process_spots_location(message: Message, state: FSMContext):
            """Обработка геолокации и отображение ближайших спотов."""
            location = await geo_service.process_location(message, state)
            if location:
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

        # Хендлер для /add_spot
        @dp.message(Command(commands=["add_spot"]))
        async def cmd_add_spot(message: Message, state: FSMContext):
            """Начало процесса добавления спота."""
            await message.answer("Введите название спота:")
            await state.set_state(AddSpotStates.entering_name)

        @dp.message(AddSpotStates.entering_name)
        async def process_spot_name(message: Message, state: FSMContext):
            """Обработка названия спота."""
            name = message.text.strip()
            if not name:
                await message.answer("Название не может быть пустым. Попробуйте снова:")
                return
            await state.update_data(name=name)
            await message.answer(
                "Отправьте геолокацию спота (используйте кнопку 'Отправить геолокацию' в Telegram):"
            )
            await state.set_state(AddSpotStates.entering_location)

        @dp.message(
            AddSpotStates.entering_location,
            ContentTypeFilter(content_types=ContentType.LOCATION),
        )
        async def process_spot_location(message: Message, state: FSMContext):
            """Обработка геолокации спота."""
            if not message.location:
                await message.answer("Пожалуйста, отправьте геолокацию.")
                return
            latitude = message.location.latitude
            longitude = message.location.longitude
            await state.update_data(latitude=latitude, longitude=longitude)
            await message.answer(
                "Введите описание спота (или отправьте /skip, чтобы пропустить):"
            )
            await state.set_state(AddSpotStates.entering_description)

        @dp.message(AddSpotStates.entering_description)
        async def process_spot_description(message: Message, state: FSMContext):
            """Обработка описания спота."""
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

        logger.info("Бот запущен")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
