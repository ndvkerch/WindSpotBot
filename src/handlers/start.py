import logging
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.keyboards.main import MainKeyboards

logger = logging.getLogger(__name__)


def register_start_handlers(dp: Dispatcher):
    """Регистрация хендлеров для команды /start."""

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
