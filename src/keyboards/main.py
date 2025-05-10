import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.models.spot import Spot, SpotWithDistance
from typing import List

logger = logging.getLogger(__name__)


class MainKeyboards:
    """Клавиатуры бота."""

    @staticmethod
    def get_main_menu() -> InlineKeyboardMarkup:
        """Получение главного меню."""
        logger.info("Создание главного меню")
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
        logger.info("Создание клавиатуры типов чек-инов")
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="На месте", callback_data="checkin:1")],
                [InlineKeyboardButton(text="Прибуду", callback_data="checkin:2")],
                [InlineKeyboardButton(text="Планирую", callback_data="checkin:3")],
                [InlineKeyboardButton(text="Назад", callback_data="back_to_spots")],
                [
                    InlineKeyboardButton(
                        text="В главное меню", callback_data="main_menu"
                    )
                ],
            ]
        )
        return kb

    @staticmethod
    def get_spot_chat_button() -> InlineKeyboardMarkup:
        """Кнопка для перехода в @WindSpotChat."""
        logger.info("Создание кнопки для чата @WindSpotChat")
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Чат спотов", url="t.me/WindSpotChat")]
            ]
        )
        return kb

    @staticmethod
    def get_subscription_options(spot_name: str) -> InlineKeyboardMarkup:
        """Клавиатура для управления подписками на спот."""
        logger.info(f"Создание клавиатуры подписок для спота '{spot_name}'")
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
    def get_spots_list(spots: List[SpotWithDistance]) -> InlineKeyboardMarkup:
        """Получение списка спотов."""
        logger.info(f"Создание клавиатуры для {len(spots)} спотов")
        inline_keyboard = []
        for spot_with_distance in spots:
            spot = spot_with_distance.spot
            distance = f"{spot_with_distance.distance:.1f} км"
            inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"{spot.name} ({distance})",
                        callback_data=f"spot:{spot.id}",
                    )
                ]
            )
        inline_keyboard.append(
            [InlineKeyboardButton(text="Назад", callback_data="back_to_location")]
        )
        inline_keyboard.append(
            [InlineKeyboardButton(text="В главное меню", callback_data="main_menu")]
        )
        kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        logger.info(f"Клавиатура спотов создана: {len(inline_keyboard)} кнопок")
        return kb

    @staticmethod
    def get_refresh_button(spot_id: int) -> InlineKeyboardMarkup:
        """Создание кнопки 'Обновить' для спота."""
        logger.info(f"Создание кнопки 'Обновить' для спота ID {spot_id}")
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔄 Обновить", callback_data=f"refresh_spot:{spot_id}"
                    )
                ]
            ]
        )
        return keyboard

    @staticmethod
    def get_activity_controls() -> InlineKeyboardMarkup:
        """Создание клавиатуры для управления активностью."""
        logger.info("Создание клавиатуры для управления активностью")
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔄 Обновить всё", callback_data="refresh_all"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📍 Обновить геопозицию", callback_data="refresh_location"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🏠 В главное меню", callback_data="main_menu"
                    )
                ],
            ]
        )
        return keyboard
