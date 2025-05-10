# -*- coding: utf-8 -*-
import asyncio
import logging
import traceback
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, BotCommand
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
from src.handlers.start import register_start_handlers
from src.handlers.activity import register_activity_handlers
from src.handlers.checkin import register_checkin_handlers

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

        # Регистрация хендлеров
        register_start_handlers(dp)
        register_activity_handlers(
            dp,
            geo_service,
            spot_service,
            checkin_service,
            weather_service,
            chat_service,
        )
        register_checkin_handlers(dp, geo_service, spot_service, checkin_service)

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
                await geo_service.request_location(message, state, user_id)
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

        # Запуск бота
        logger.info("Бот запущен")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
