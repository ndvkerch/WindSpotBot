from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from src.models.spot import Spot
from typing import List
import logging

logger = logging.getLogger(__name__)


class MainKeyboards:
    """Клавиатуры бота."""

    @staticmethod
    def get_main_menu() -> InlineKeyboardMarkup:
        """Получение главного меню."""
        logger.debug("Создание главного меню")
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Чек-ин", callback_data="checkin")],
                [InlineKeyboardButton(text="Ближайшие споты", callback_data="spots")],
                [InlineKeyboardButton(text="Активность", callback_data="activity")],
                [InlineKeyboardButton(text="Добавить спот", callback_data="add_spot")],
            ]
        )
        return kb

    @staticmethod
    def get_checkin_types() -> InlineKeyboardMarkup:
        """Клавиатура для типов чек-инов."""
        logger.debug("Создание клавиатуры типов чек-инов")
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
        logger.debug("Создание кнопки для чата @WindSpotChat")
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Чат спотов", url="t.me/WindSpotChat")]
            ]
        )
        return kb

    @staticmethod
    def get_subscription_options(spot_name: str) -> InlineKeyboardMarkup:
        """Клавиатура для управления подписками на спот."""
        logger.debug(f"Создание клавиатуры подписок для спота '{spot_name}'")
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
    def get_spots_list(spots: List[Spot]) -> InlineKeyboardMarkup:
        """Получение списка спотов."""
        logger.info(f"Создание клавиатуры для {len(spots)} спотов")
        inline_keyboard = []
        for spot in spots:
            distance = f"{spot.distance:.1f} км" if hasattr(spot, "distance") else "N/A"
            inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"{spot.name} ({distance})",
                        callback_data=f"spot:{spot.id}",
                    )
                ]
            )
        kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        logger.debug(f"Клавиатура спотов создана: {len(inline_keyboard)} кнопок")
        return kb
