from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_checkin_duration_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора длительности чек-ина."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    durations = ["1 час", "2 часа", "3 часа", "4 часа", "5 часов", "6 часов"]
    buttons = [InlineKeyboardButton(text=d, callback_data=f"duration:{d}") for d in durations]
    keyboard.add(*buttons)
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back"))
    return keyboard

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Основное меню."""
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text="✅ Чек-ин", callback_data="checkin"),
        InlineKeyboardButton(text="🔍 Кто на спотах", callback_data="spots"),
        InlineKeyboardButton(text="🌊 Погода", callback_data="weather"),
        InlineKeyboardButton(text="📅 Планирование", callback_data="plan"),
    ]
    keyboard.add(*buttons)
    return keyboard