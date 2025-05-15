import asyncio
import logging
import traceback
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import BotCommand, Message
from aiogram.client.default import DefaultBotProperties
from src.config.config import settings
from src.database.init import init_db
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
from src.repositories.user import UserRepository
from src.handlers.start import register_start_handlers
from src.handlers.activity import register_activity_handlers
from src.handlers.checkin import register_checkin_handlers
from src.handlers.main_menu import register_main_menu_handlers
from src.services.scheduler import SchedulerService
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiosqlite
import aiohttp

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    """Инициализация и запуск бота."""
    logger.info("Инициализация модуля bot.py")
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    http_session = None
    scheduler = AsyncIOScheduler()

    try:
        await bot.set_my_commands(
            [
                BotCommand(command="/start", description="Запустить бота"),
                BotCommand(command="/checkin", description="Чек-ин на споте"),
                BotCommand(command="/spots", description="Посмотреть ближайшие споты"),
                BotCommand(command="/activity", description="Активность на спотах"),
                BotCommand(command="/add_spot", description="Добавить новый спот"),
                BotCommand(
                    command="/subscribe", description="Подписаться на уведомления"
                ),
                BotCommand(
                    command="/create_topic", description="Создать тему для спота"
                ),
                BotCommand(
                    command="/test_notification", description="Тест уведомления"
                ),
                BotCommand(command="/test_chat", description="Тест сообщения в чат"),
            ]
        )

        async with aiosqlite.connect("data/database.db") as db:
            await init_db("data/database.db")
            user_repo = UserRepository(db)
            subscription_repo = SubscriptionRepository(db)
            spot_repo = SpotRepository(db)
            checkin_repo = CheckinRepository(db)
            geo_service = GeoService(bot)
            topic_service = TopicService(bot, db)
            http_session = aiohttp.ClientSession()
            notification_service = NotificationService(
                bot, topic_service, subscription_repo
            )
            chat_service = ChatService(bot, topic_service, notification_service)
            spot_service = SpotService(spot_repo, geo_service)
            weather_service = WeatherService(http_session=http_session)
            checkin_service = CheckinService(
                bot,
                checkin_repo,
                notification_service,
                spot_service,
                user_repo,
                weather_service,
            )
            scheduler_service = SchedulerService(scheduler, checkin_service)

            # Добавление middleware для инъекции зависимостей
            async def inject_dependencies_middleware(handler, event, data):
                data["checkin_repo"] = checkin_repo
                data["user_repo"] = user_repo
                data["geo_service"] = geo_service
                data["spot_service"] = spot_service
                data["checkin_service"] = checkin_service
                data["weather_service"] = weather_service
                data["chat_service"] = chat_service
                return await handler(event, data)

            dp.update.middleware(inject_dependencies_middleware)

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

            register_start_handlers(dp)
            register_activity_handlers(
                dp,
                geo_service=geo_service,
                spot_service=spot_service,
                checkin_service=checkin_service,
                weather_service=weather_service,
                chat_service=chat_service,
            )
            register_checkin_handlers(
                dp,
                geo_service=geo_service,
                spot_service=spot_service,
                checkin_service=checkin_service,
            )
            register_main_menu_handlers(dp)

            @dp.message(Command(commands=["create_topic"]))
            async def cmd_create_topic(message: Message, topic_service: TopicService = None):
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

            @dp.message(Command(commands=["subscribe"]))
            async def cmd_subscribe(message: Message, subscription_repo: SubscriptionRepository = None):
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

            @dp.message(Command(commands=["test_notification"]))
            async def cmd_test_notification(message: Message, notification_service: NotificationService = None):
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

            @dp.message(Command(commands=["test_chat"]))
            async def cmd_test_chat(message: Message, chat_service: ChatService = None):
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
                        await message.answer(
                            f"Ошибка при отправке в тему '{spot_name}'"
                        )
                except Exception as e:
                    logger.error(f"Ошибка в cmd_test_chat: {e}")
                    await message.answer(f"Не удалось отправить сообщение: {e}")

            # Запуск планировщика
            scheduler_service.start()
            scheduler_service.add_checkin_expiration_job(interval_minutes=5)
            scheduler_service.add_checkin_warning_job(interval_minutes=2)
            scheduler_service.add_pending_checkin_notification_job(interval_minutes=2)
            scheduler_service.add_delete_expired_type_2_checkins_job(interval_minutes=5)

            logger.info("Бот запущен")
            await dp.start_polling(bot)

    finally:
        if http_session and not http_session.closed:
            await http_session.close()
        await weather_service.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
