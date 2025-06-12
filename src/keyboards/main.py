import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.models.spot import Spot, SpotWithDistance
from src.repositories.checkin import CheckinRepository
from typing import List
from datetime import date, timedelta

logger = logging.getLogger(__name__)

class MainKeyboards:
    """Клавиатуры бота."""

    @staticmethod
    async def get_main_menu(user_id: int, checkin_repo: CheckinRepository) -> InlineKeyboardMarkup:
        """Получение главного меню с динамическими кнопками для активных чек-инов."""
        logger.info(f"Создание главного меню для пользователя {user_id}")
        builder = InlineKeyboardBuilder()
        buttons = [
            InlineKeyboardButton(text="🏄‍♂️ Отметится на споте", callback_data="checkin"),
            InlineKeyboardButton(text="🌊 Ближайшие споты", callback_data="spots"),
            InlineKeyboardButton(text="💨 Кто на спотах", callback_data="activity"),
            InlineKeyboardButton(text="🪁 Добавить спот", callback_data="add_spot"),
            InlineKeyboardButton(text="⭐ Избранные споты", callback_data="favorites"),
            InlineKeyboardButton(text="📅 Планирование", callback_data="plan"),
            InlineKeyboardButton(text="📊 Профиль", callback_data="profile"),
        ]
        for button in buttons:
            builder.add(button)

        active_checkins = await checkin_repo.get_by_user(user_id)
        for checkin in active_checkins:
            if checkin.active:
                if checkin.type == 2:
                    builder.add(
                        InlineKeyboardButton(
                            text="✅ Я на месте",
                            callback_data=f"confirm_arrival:{checkin.id}",
                        )
                    )
                    builder.add(
                        InlineKeyboardButton(
                            text="❌ Не приеду",
                            callback_data=f"cancel_checkin:{checkin.id}",
                        )
                    )
                elif checkin.type == 1:  # Тип 1
                    builder.add(
                        InlineKeyboardButton(
                            text="🚪 Покинуть спот",
                            callback_data=f"leave_spot:{checkin.id}",
                        )
                    )

        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def get_post_checkin_menu(checkin_id: int) -> InlineKeyboardMarkup:
        """Клавиатура после чек-ина."""
        logger.info(f"Создание клавиатуры после чек-ина #{checkin_id}")
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text="🚪 Покинуть спот",
                callback_data=f"leave_spot:{checkin_id}",
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="🏠 В главное меню",
                callback_data="main_menu",
            )
        )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_checkin_types() -> InlineKeyboardMarkup:
        """Клавиатура для типов чек-инов."""
        logger.info("Создание клавиатуры типов чек-инов")
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="✅ На месте", callback_data="checkin:1"))
        builder.add(InlineKeyboardButton(text="⏳ Прибуду", callback_data="checkin:2"))
        builder.add(InlineKeyboardButton(text="📅 Планирую", callback_data="checkin:3"))
        builder.add(InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_spots"))
        builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu"))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_duration_options() -> InlineKeyboardMarkup:
        """Клавиатура для выбора длительности чек-ина."""
        logger.info("Создание клавиатуры длительности чек-ина")
        builder = InlineKeyboardBuilder()
        durations = [(1, "1 час"), (2, "2 часа"), (3, "3 часа"), (4, "4 часа"), (5, "5 часов"), (6, "6 часов")]
        for hours, text in durations:
            builder.add(InlineKeyboardButton(text=text, callback_data=f"duration:{hours}"))
        builder.add(InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_type"))
        builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu"))
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def get_planned_time_options() -> InlineKeyboardMarkup:
        """Клавиатура для выбора времени прибытия для чек-ина 2-го типа."""
        logger.info("Создание клавиатуры времени прибытия")
        builder = InlineKeyboardBuilder()
        times = [(1, "Через 1 час"), (2, "Через 2 часа"), (3, "Через 3 часа")]
        for hours, text in times:
            builder.add(InlineKeyboardButton(text=text, callback_data=f"planned_time:{hours}"))
        builder.add(InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_type"))
        builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu"))
        builder.adjust(3, 2)
        return builder.as_markup()

    @staticmethod
    def get_confirm_arrival_menu(checkin_id: int) -> InlineKeyboardMarkup:
        """Клавиатура для подтверждения прибытия на спот."""
        logger.info(f"Создание клавиатуры подтверждения прибытия для чек-ина #{checkin_id}")
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text="✅ Я на месте",
                callback_data=f"confirm_arrival:{checkin_id}",
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="❌ Не приеду",
                callback_data=f"cancel_checkin:{checkin_id}",
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="🏠 В главное меню",
                callback_data="main_menu",
            )
        )
        builder.adjust(2, 1)
        return builder.as_markup()

    @staticmethod
    def get_extend_checkin_menu(checkin_id: int) -> InlineKeyboardMarkup:
        """Клавиатура для продления чек-ина."""
        logger.info(f"Создание клавиатуры продления для чек-ина #{checkin_id}")
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text="⏳ Продлить на 1 час",
                callback_data=f"extend_checkin:{checkin_id}",
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="🏠 В главное меню",
                callback_data="main_menu",
            )
        )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_spot_chat_button() -> InlineKeyboardMarkup:
        """Кнопка для перехода в @WindSpotChat."""
        logger.info("Создание кнопки для чата @WindSpotChat")
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="Чат спотов", url="t.me/WindSpotChat"))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_subscription_options(spot_name: str) -> InlineKeyboardMarkup:
        """Клавиатура для управления подписками на спот."""
        logger.info(f"Создание клавиатуры подписок для спота '{spot_name}'")
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text="Подписаться на чек-ины",
                callback_data=f"subscribe:{spot_name}:checkin",
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="Подписаться на сообщения",
                callback_data=f"subscribe:{spot_name}:message",
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="Подписаться на погоду",
                callback_data=f"subscribe:{spot_name}:weather",
            )
        )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_spots_list(spots: List[SpotWithDistance]) -> InlineKeyboardMarkup:
        """Получение списка спотов."""
        logger.info(f"Создание клавиатуры для {len(spots)} спотов")
        builder = InlineKeyboardBuilder()
        for spot_with_distance in spots:
            spot = spot_with_distance.spot
            distance = f"{spot_with_distance.distance:.1f} км"
            builder.add(
                InlineKeyboardButton(
                    text=f"{spot.name} ({distance})",
                    callback_data=f"spot:{spot.id}",
                )
            )
        builder.add(InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_location"))
        builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu"))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_refresh_button(spot_id: int) -> InlineKeyboardMarkup:
        """Создание кнопки 'Обновить' для спота."""
        logger.info(f"Создание кнопки 'Обновить' для спота ID {spot_id}")
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text="🔄 Обновить",
                callback_data=f"refresh_spot:{spot_id}",
            )
        )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_activity_controls() -> InlineKeyboardMarkup:
        """Создание клавиатуры для управления активностью."""
        logger.info("Создание клавиатуры для управления активностью")
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="📍 Уточнить геопозицию", callback_data="refresh_location"))
        builder.add(InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_all"))
        builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu"))
        builder.adjust(1, 2)
        return builder.as_markup()

    @staticmethod
    def get_date_options() -> InlineKeyboardMarkup:
        """Клавиатура для выбора даты поездки для чек-ина типа 3."""
        logger.info("Создание клавиатуры выбора даты")
        builder = InlineKeyboardBuilder()
        today = date.today()
        for i in range(1, 8):  # Следующие 7 дней
            day = today + timedelta(days=i)
            builder.add(
                InlineKeyboardButton(
                    text=day.strftime("%d.%m.%Y"),
                    callback_data=f"date:{day.isoformat()}",
                )
            )
        builder.add(InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_type"))
        builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu"))
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def get_confirm_planned_checkin() -> InlineKeyboardMarkup:
        """Клавиатура для подтверждения чек-ина типа 3."""
        logger.info("Создание клавиатуры подтверждения плана")
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text="✅ Подтвердить",
                callback_data="confirm_plan",
            )
        )
        builder.add(InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_date"))
        builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu"))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_cancel_planned_menu(checkin_id: int) -> InlineKeyboardMarkup:
        """Клавиатура для отмены чек-ина типа 3."""
        logger.info(f"Создание клавиатуры отмены плана для чек-ина #{checkin_id}")
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text="❌ Отменить планы",
                callback_data=f"cancel_checkin:{checkin_id}",
            )
        )
        builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu"))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_planned_checkin_reminder_menu(checkin_id: int) -> InlineKeyboardMarkup:
        """Клавиатура для напоминаний о чек-ине типа 3."""
        logger.info(f"Создание клавиатуры напоминания для чек-ина #{checkin_id}")
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text="✅ Чек-ин на месте",
                callback_data=f"planned_action:type1_{checkin_id}",
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="⏳ Планирую приехать",
                callback_data=f"planned_action:type2_{checkin_id}",
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="❌ Отменить планы",
                callback_data=f"planned_action:cancel_{checkin_id}",
            )
        )
        builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu"))
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def get_empty_plans_menu() -> InlineKeyboardMarkup:
        """Клавиатура для пустого списка планов."""
        logger.info("Создание клавиатуры для пустого списка планов")
        kb = InlineKeyboardBuilder()
        kb.button(text="🔄 Обновить", callback_data="refresh_plan")
        kb.button(text="↩️ В главное меню", callback_data="main_menu")
        kb.adjust(2)
        kb_markup = kb.as_markup()
        logger.debug(f"Клавиатура пустого списка планов: {kb_markup.inline_keyboard}")
        return kb_markup

    @staticmethod
    def get_plans_menu(checkin_ids: list[int]) -> InlineKeyboardMarkup:
        """Клавиатура для списка запланированных чек-инов."""
        logger.info(f"Создание клавиатуры для списка планов с {len(checkin_ids)} чек-инами")
        kb = InlineKeyboardBuilder()
        for i, checkin_id in enumerate(checkin_ids, 1):
            kb.button(text=f"❌ Отменить план {i}", callback_data=f"cancel_plan:{checkin_id}")
        kb.button(text="🔄 Обновить", callback_data="refresh_plan")
        kb.button(text="↩️ В главное меню", callback_data="main_menu")
        # Явно задаём компоновку: по 1 кнопке для отмены, затем 2 кнопки для управления
        adjust_values = [1] * len(checkin_ids) + [2]
        kb.adjust(*adjust_values)
        kb_markup = kb.as_markup()
        logger.debug(f"Клавиатура списка планов: {kb_markup.inline_keyboard}")
        return kb_markup
