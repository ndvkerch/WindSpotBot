from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


class MainKeyboards:
    """Клавиатуры для основного интерфейса бота."""

    @staticmethod
    def get_main_menu() -> ReplyKeyboardMarkup:
        """Основное меню."""
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(KeyboardButton("Найти споты"))
        kb.add(KeyboardButton("Мои чек-ины"))
        kb.add(KeyboardButton("Топ спотов"))
        kb.add(KeyboardButton("Мои подписки"))
        return kb

    @staticmethod
    def get_checkin_types() -> InlineKeyboardMarkup:
        """Клавиатура для типов чек-инов."""
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("На месте", callback_data="checkin:1"))
        kb.add(InlineKeyboardButton("Прибуду", callback_data="checkin:2"))
        kb.add(InlineKeyboardButton("Планирую", callback_data="checkin:3"))
        return kb

    @staticmethod
    def get_spot_chat_button() -> InlineKeyboardMarkup:
        """Кнопка для перехода в @WindSpotChat."""
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Чат спотов", url="t.me/WindSpotChat"))
        return kb

    @staticmethod
    def get_subscription_options(spot_name: str) -> InlineKeyboardMarkup:
        """Клавиатура для управления подписками на спот."""
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton(
                "Подписаться на чек-ины", callback_data=f"subscribe:{spot_name}:checkin"
            )
        )
        kb.add(
            InlineKeyboardButton(
                "Подписаться на сообщения",
                callback_data=f"subscribe:{spot_name}:message",
            )
        )
        kb.add(
            InlineKeyboardButton(
                "Подписаться на погоду", callback_data=f"subscribe:{spot_name}:weather"
            )
        )
        return kb
