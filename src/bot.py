import asyncio
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from src.config.config import settings
from src.services.topic import TopicService
from src.services.notification import NotificationService
from src.services.chat import ChatService
from src.repositories.subscription import SubscriptionRepository
from src.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Запуск бота."""
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Инициализация БД
    async with aiosqlite.connect("data/database.db") as db:
        # Инициализация сервисов
        subscription_repo = SubscriptionRepository(db)
        topic_service = TopicService(bot, db)
        notification_service = NotificationService(
            bot, topic_service, subscription_repo
        )
        chat_service = ChatService(bot, topic_service, notification_service)

        # Хендлер для создания темы
        @dp.message(Command(commands=["create_topic"]))
        async def cmd_create_topic(message: types.Message):
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
                    await message.answer(f"Ошибка при создании темы '{spot_name}'")
            except Exception as e:
                logger.error(f"Ошибка в cmd_create_topic: {e}")
                await message.answer(f"Не удалось создать тему: {e}")

        # Хендлер для подписки (тест)
        @dp.message(Command(commands=["subscribe"]))
        async def cmd_subscribe(message: types.Message):
            """Тестовая подписка на события."""
            try:
                parts = message.text.split(maxsplit=2)
                if len(parts) < 3:
                    await message.answer(
                        "Использование: /subscribe <spot_name> <event_type>"
                    )
                    return
                spot_name, event_type = parts[1], parts[2]
                if event_type not in ["checkin", "message", "weather"]:
                    await message.answer(
                        "Неверный тип события: checkin, message, weather"
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
        async def cmd_test_notification(message: types.Message):
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
        async def cmd_test_chat(message: types.Message):
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

        # Временный хендлер для получения message_thread_id
        @dp.message()
        async def get_topic_id(message: types.Message):
            """Получение message_thread_id темы."""
            thread_id = message.message_thread_id
            if thread_id:
                await message.answer(f"Topic ID для темы: {thread_id}")
            else:
                await message.answer("Это не тема или thread_id отсутствует.")

        logger.info("Бот запущен")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
