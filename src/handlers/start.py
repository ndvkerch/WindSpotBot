import logging
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.keyboards.main import MainKeyboards
from src.models.user import User
from src.repositories.user import UserRepository
from src.services.geo import GeoService

logger = logging.getLogger(__name__)


class StartStates(StatesGroup):
    requesting_location = State()


def register_start_handlers(
    dp: Dispatcher, user_repo: UserRepository, geo_service: GeoService
):
    """Регистрация обработчиков для команды /start."""

    @dp.message(Command(commands=["start"]))
    async def cmd_start(message: Message, state: FSMContext):
        """Обработка команды /start."""
        user_id = message.from_user.id
        logger.info(f"Команда /start от пользователя {user_id}")

        # Создание или обновление пользователя
        await user_repo.create(
            user_id=user_id,
            name=message.from_user.full_name,
            username=message.from_user.username,
        )

        # Приветственное сообщение
        await message.answer(
            f"🤙 Йо, {message.from_user.full_name}! Добро пожаловать на борт WindSpotBot! 🏄‍♂️\n"
            "Лови ветер, находи споты и тусуйся с кайтерами! 💨\n"
            "💬 Заходи в @WindSpotRU, там волна новостей и движухи!"
        )

        # Проверка, есть ли часовой пояс
        db_user = await user_repo.get_by_id(user_id)
        if db_user and db_user.timezone:
            # Показ главного меню
            kb = MainKeyboards.get_main_menu()
            await message.answer("Выберите действие:", reply_markup=kb)
            await state.clear()
        else:
            # Запрос геолокации
            await geo_service.request_location(message, state, user_id)
            await state.set_state(StartStates.requesting_location)

    @dp.message(StartStates.requesting_location)
    async def process_start_location(
        message: Message,
        state: FSMContext,
        user_repo: UserRepository,
        geo_service: GeoService,
    ):
        """Обработка геолокации для команды /start."""
        user_id = message.from_user.id
        logger.info(f"Получена геолокация для /start от пользователя {user_id}")

        if not message.location:
            await message.answer(
                "🌊 Упс, волна унесла твою геолокацию! 😎 Отправь ещё раз, бро!"
            )
            return

        latitude = message.location.latitude
        longitude = message.location.longitude
        timezone = await geo_service.get_timezone(latitude, longitude)

        # Обновление пользователя с часовым поясом
        await user_repo.create(
            user_id=user_id,
            name=message.from_user.full_name,
            username=message.from_user.username,
            timezone=timezone,
        )

        # Показ главного меню
        kb = MainKeyboards.get_main_menu()
        await message.answer(
            "Часовой пояс сохранён! Выберите действие:", reply_markup=kb
        )
        await state.clear()
