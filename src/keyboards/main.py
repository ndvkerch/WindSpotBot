from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from typing import List


class MainKeyboards:
    """Клавиатуры для основного интерфейса бота."""

    @staticmethod
    def get_main_menu() -> ReplyKeyboardMarkup:
        """Основное меню."""
        buttons = [
            [KeyboardButton(text="Найти споты")],
            [KeyboardButton(text="Мои чек-ины")],
            [KeyboardButton(text="Топ спотов")],
            [KeyboardButton(text="Мои подписки")],
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    @staticmethod
    def get_checkin_types() -> InlineKeyboardMarkup:
        """Клавиатура для типов чек-инов."""
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="На месте", callback_data="checkin:1")],
                [InlineKeyboardButton(text="Прибуду", callback_data="checkin:2")],
                [InlineKeyboardButton(text="Планирую", callback_data="checkin:3")],
            ]
        )
        return kb

    @staticmethod
    def get_spot_chat_button() -> InlineKeyboardMarkup:
        """Кнопка для перехода в @WindSpotChat."""
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Чат спотов", url="t.me/WindSpotChat")]
            ]
        )
        return kb

    @staticmethod
    def get_subscription_options(spot_name: str) -> InlineKeyboardMarkup:
        """Клавиатура для управления подписками на спот."""
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Подписаться на чек-ины",
                        callback_data=f"subscribe:{spot_name}:checkin",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Подписаться на сообщения",
                        callback_data=f"subscribe:{spot_name}:message",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Подписаться на погоду",
                        callback_data=f"subscribe:{spot_name}:weather",
                    )
                ],
            ]
        )
        return kb

    @staticmethod
    def get_spots_list(spots: List) -> InlineKeyboardMarkup:
        """Клавиатура со списком спотов."""
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=spot.name, callback_data=f"spot:{spot.name}"
                    )
                ]
                for spot in spots
            ]
        )
        return kb
