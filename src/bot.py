import asyncio
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CallbackQueryFilter
from src.config.config import settings
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
        topic_service = TopicService(bot, db)
        notification_service = NotificationService(
            bot, topic_service, subscription_repo
        )
        chat_service = ChatService(bot, topic_service, notification_service)
        spot_service = SpotService(spot_repo)
        checkin_service = CheckinService(
            bot, checkin_repo, notification_service, spot_service
        )

        # Хендлер для /start
        @dp.message(Command(commands=["start"]))
        async def cmd_start(message: types.Message):
            """Обработка команды /start."""
            kb = MainKeyboards.get_main_menu()
            await message.answer(
                "Добро пожаловать в WindSpotBot! 🏄‍♂️\n"
                "Найдите споты для виндсёрфинга, отметьтесь или подпишитесь на уведомления!",
                reply_markup=kb,
            )

        # Хендлер для списка спотов
        @dp.message(Command(commands=["spots"]))
        async def cmd_spots(message: types.Message):
            """Отображение списка спотов."""
            try:
                spots = await spot_service.get_all_spots()
                if not spots:
                    await message.answer(
                        "Споты не найдены. Добавьте споты через /add_spot."
                    )
                    return
                kb = MainKeyboards.get_spots_list(spots)
                await message.answer("Выберите спот:", reply_markup=kb)
            except Exception as e:
                logger.error(f"Ошибка в cmd_spots: {e}")
                await message.answer(f"Не удалось загрузить споты: {e}")

        # Callback-обработчик для выбора спота
        @dp.callback_query(CallbackQueryFilter(lambda c: c.data.startswith("spot:")))
        async def callback_spot(callback: types.CallbackQuery):
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
                # Сохраняем spot_id в callback.data
                callback.data = f"checkin:{spot.id}"
                await callback.answer()
            except Exception as e:
                logger.error(f"Ошибка в callback_spot: {e}")
                await callback.answer(f"Ошибка: {e}", show_alert=True)

        # Callback-обработчик для чек-ина
        @dp.callback_query(CallbackQueryFilter(lambda c: c.data.startswith("checkin:")))
        async def callback_checkin(callback: types.CallbackQuery):
            """Обработка чек-ина."""
            try:
                spot_id = int(callback.data.split(":", 1)[1])
                checkin_type = int(
                    callback.message.reply_markup.inline_keyboard[0][
                        0
                    ].callback_data.split(":")[1]
                )
                user = User(
                    id=callback.from_user.id,
                    name=callback.from_user.full_name,
                    username=callback.from_user.username,
                )
                success = await checkin_service.create_checkin(
                    user, spot_id, checkin_type
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
                await callback.answer()
            except Exception as e:
                logger.error(f"Ошибка в callback_checkin: {e}")
                await callback.answer(f"Ошибка: {e}", show_alert=True)

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
                    await message.answer(f"Ошибка при создания темы '{spot_name}'")
            except Exception as e:
                logger.error(f"Ошибка в cmd_create_topic: {e}")
                await message.answer(f"Не удалось создать тему: {e}")

        # Хендлер для подписки
        @dp.message(Command(commands=["subscribe"]))
        async def cmd_subscribe(message: types.Message):
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

        logger.info("Бот запущен")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
