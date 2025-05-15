import logging
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.services.geo import GeoService
from src.services.spot import SpotService
from src.services.checkin import CheckinService
from src.models.user import User
from src.keyboards.main import MainKeyboards
from datetime import datetime, timedelta, date

logger = logging.getLogger(__name__)

class CheckinStates(StatesGroup):
    """Состояния для процесса чек-ина."""
    requesting_location = State()
    selecting_spot = State()
    selecting_type = State()
    selecting_duration = State()
    selecting_planned_time = State()
    confirming_duration = State()
    selecting_date = State()  # Состояние для выбора даты
    confirming_planned_checkin = State()  # Состояние для подтверждения чек-ина типа 3

def register_checkin_handlers(
    dp: Dispatcher,
    geo_service: GeoService,
    spot_service: SpotService,
    checkin_service: CheckinService,
):
    """Регистрация хендлеров для команды /checkin."""

    @dp.message(Command(commands=["checkin"]))
    async def cmd_checkin(message: Message, state: FSMContext, user_id: int = None):
        """Обработка команды /checkin."""
        user_id = user_id or message.from_user.id
        logger.info(f"Команда /checkin от пользователя {user_id}")
        await state.clear()
        cached_location = await geo_service.get_cached_location(user_id)
        if cached_location:
            latitude, longitude = cached_location
            logger.info(f"Использован кэш: ({latitude}, {longitude})")
            spots = await spot_service.get_all_spots()
            nearby_spots = await geo_service.get_nearby_spots(
                spots, latitude, longitude
            )
            if not nearby_spots:
                await message.answer(
                    "🤙 Йо, споты не найдены! Добавь новый через /add_spot! 🪁"
                )
                return
            kb = MainKeyboards.get_spots_list(nearby_spots)
            await state.update_data(latitude=latitude, longitude=longitude)
            await message.answer("🏄‍♂️ Выбери спот для чек-ина:", reply_markup=kb)
            await state.set_state(CheckinStates.selecting_spot)
        else:
            await geo_service.request_location(message, state, user_id)
            await state.set_state(CheckinStates.requesting_location)

    @dp.message(CheckinStates.requesting_location)
    async def process_checkin_location(message: Message, state: FSMContext):
        """Обработка геолокации для чек-ина."""
        user_id = message.from_user.id
        logger.info(f"Обработка геолокации для чек-ина от пользователя {user_id}")
        if not message.location:
            logger.warning("Получен неверный тип контента: не геолокация")
            await message.answer("🤙 Йо, отправь геолокацию, бро! 📍")
            return
        latitude = message.location.latitude
        longitude = message.location.longitude
        await geo_service.cache_location(user_id, latitude, longitude)
        logger.info(f"Получена геолокация: ({latitude}, {longitude})")
        spots = await spot_service.get_all_spots()
        nearby_spots = await geo_service.get_nearby_spots(spots, latitude, longitude)
        if not nearby_spots:
            await message.answer(
                "🤙 Йо, споты не найдены! Добавь новый через /add_spot! 🪁"
            )
            await state.clear()
            return
        kb = MainKeyboards.get_spots_list(nearby_spots)
        await state.update_data(latitude=latitude, longitude=longitude)
        await message.answer("🏄‍♂️ Выбери спот для чек-ина:", reply_markup=kb)
        await state.set_state(CheckinStates.selecting_spot)

    @dp.callback_query(
        lambda c: c.data and c.data.startswith("spot:"), CheckinStates.selecting_spot
    )
    async def callback_spot(callback: CallbackQuery, state: FSMContext):
        """Обработка выбора спота."""
        user_id = callback.from_user.id
        logger.info(f"Выбор спота: {callback.data} пользователем {user_id}")
        try:
            spot_id = int(callback.data.split(":", 1)[1])
            spot = await spot_service.get_spot_by_id(spot_id)
            if not spot:
                await callback.message.edit_text(
                    f"🤙 Спот с ID {spot_id} не найден, бро! 😕"
                )
                await state.clear()
                return
            kb = MainKeyboards.get_checkin_types()
            await callback.message.edit_text(
                f"🏄‍♂️ Йо, ты выбрал '{spot.name}'! Какой вайб? 💨", reply_markup=kb
            )
            await state.update_data(spot_id=spot.id, spot_name=spot.name)
            await state.set_state(CheckinStates.selecting_type)
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_spot: {e}")
            await callback.message.edit_text(f"😕 Ошибка при выборе спота: {str(e)}")
            await state.clear()

    @dp.callback_query(
        lambda c: c.data and c.data.startswith("checkin:"), CheckinStates.selecting_type
    )
    async def callback_checkin_type(callback: CallbackQuery, state: FSMContext):
        """Обработка выбора типа чек-ина."""
        user_id = callback.from_user.id
        logger.info(f"Выбор типа чек-ина: {callback.data} пользователем {user_id}")
        try:
            data = await state.get_data()
            spot_id = data.get("spot_id")
            spot_name = data.get("spot_name")
            if not spot_id:
                await callback.message.edit_text("😕 Ошибка: спот не выбран, бро!")
                await state.clear()
                return
            checkin_type = int(callback.data.split(":", 1)[1])
            user = User(
                id=user_id,
                name=callback.from_user.full_name,
                username=callback.from_user.username,
            )
            if checkin_type == 1:  # На месте
                kb = MainKeyboards.get_duration_options()
                await callback.message.edit_text(
                    f"✅ Йо, ты на '{spot_name}'! Лови вайб! 🏄‍♂️\nСколько тусить будешь?",
                    reply_markup=kb,
                )
                await state.update_data(checkin_type=checkin_type)
                await state.set_state(CheckinStates.selecting_duration)
            elif checkin_type == 2:  # Прибуду позже
                kb = MainKeyboards.get_planned_time_options()
                await callback.message.edit_text(
                    f"📅 Йо, когда планируешь быть на '{spot_name}'? 🏄‍♂️",
                    reply_markup=kb,
                )
                await state.update_data(checkin_type=checkin_type)
                await state.set_state(CheckinStates.selecting_planned_time)
            elif checkin_type == 3:  # Планирую
                kb = MainKeyboards.get_date_options()
                await callback.message.edit_text(
                    f"📅 Шаг 2/2: Выбери дату поездки на '{spot_name}':",
                    reply_markup=kb,
                )
                await state.update_data(checkin_type=checkin_type)
                await state.set_state(CheckinStates.selecting_date)
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_checkin_type: {e}")
            await callback.message.edit_text(f"😕 Ошибка при чек-ине: {str(e)}")
            await state.clear()

    @dp.callback_query(
        lambda c: c.data and c.data.startswith("date:"), CheckinStates.selecting_date
    )
    async def callback_date(callback: CallbackQuery, state: FSMContext):
        """Обработка выбора даты для чек-ина типа 3."""
        user_id = callback.from_user.id
        logger.info(f"Выбор даты: {callback.data} пользователем {user_id}")
        try:
            data = await state.get_data()
            spot_name = data.get("spot_name")
            if not spot_name:
                await callback.message.edit_text("😕 Ошибка: спот не выбран, бро!")
                await state.clear()
                return
            date_str = callback.data.split(":", 1)[1]
            planned_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            kb = MainKeyboards.get_confirm_planned_checkin()
            await callback.message.edit_text(
                f"📅 Ты планируешь посетить '{spot_name}' {planned_date.strftime('%d.%m.%Y')}?",
                reply_markup=kb,
            )
            await state.update_data(planned_date=planned_date)
            await state.set_state(CheckinStates.confirming_planned_checkin)
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_date: {e}")
            await callback.message.edit_text(f"😕 Ошибка при выборе даты: {str(e)}")
            await state.clear()

    @dp.callback_query(
        lambda c: c.data == "confirm_plan", CheckinStates.confirming_planned_checkin
    )
    async def callback_confirm_plan(callback: CallbackQuery, state: FSMContext):
        """Подтверждение чек-ина типа 3."""
        user_id = callback.from_user.id
        logger.info(f"Подтверждение плана пользователем {user_id}")
        try:
            data = await state.get_data()
            spot_id = data.get("spot_id")
            spot_name = data.get("spot_name")
            planned_date = data.get("planned_date")
            if not spot_id or not planned_date:
                await callback.message.edit_text("😕 Ошибка: данные не найдены, бро!")
                await state.clear()
                return
            user = User(
                id=user_id,
                name=callback.from_user.full_name,
                username=callback.from_user.username,
            )
            success = await checkin_service.create_checkin(
                user, spot_id, checkin_type=3, planned_date=planned_date
            )
            if success:
                date_text = planned_date.strftime("%d.%m.%Y")
                checkin = (await checkin_service.checkin_repo.get_by_user(user_id))[-1]  # Последний чек-ин
                await callback.message.edit_text(
                    f"✅ Планы на '{spot_name}' {date_text} сохранены, бро! 🏄‍♂️",
                    reply_markup=MainKeyboards.get_cancel_planned_menu(checkin.id),
                )
            else:
                await callback.message.edit_text(
                    f"😕 Не удалось запланировать тусу на '{spot_name}', бро!"
                )
            await state.clear()
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_confirm_plan: {e}")
            await callback.message.edit_text(f"😕 Ошибка при подтверждении плана: {str(e)}")
            await state.clear()

    @dp.callback_query(
        lambda c: c.data and c.data.startswith("duration:"), CheckinStates.selecting_duration
    )
    async def callback_duration(callback: CallbackQuery, state: FSMContext):
        """Обработка выбора длительности чек-ина."""
        user_id = callback.from_user.id
        logger.info(f"Выбор длительности: {callback.data} пользователем {user_id}")
        try:
            data = await state.get_data()
            spot_id = data.get("spot_id")
            checkin_type = data.get("checkin_type")
            if not spot_id or not checkin_type:
                await callback.message.edit_text("😕 Ошибка: данные не найдены, бро!")
                await state.clear()
                return
            duration_hours = int(callback.data.split(":", 1)[1])
            duration_seconds = duration_hours * 3600
            user = User(
                id=user_id,
                name=callback.from_user.full_name,
                username=callback.from_user.username,
            )
            success = await checkin_service.create_checkin(
                user, spot_id, checkin_type, duration=duration_seconds
            )
            if success:
                await callback.message.edit_text(
                    f"✅ Чек-ин на '{data.get('spot_name')}' на {duration_hours} ч создан, бро! 🏄‍♂️"
                )
            else:
                await callback.message.edit_text(
                    f"😕 Не удалось создать чек-ин на '{data.get('spot_name')}', бро!"
                )
            await state.clear()
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_duration: {e}")
            await callback.message.edit_text(
                f"😕 Ошибка при выборе длительности: {str(e)}"
            )
            await state.clear()

    @dp.callback_query(
        lambda c: c.data and c.data.startswith("planned_time:"), CheckinStates.selecting_planned_time
    )
    async def callback_planned_time(callback: CallbackQuery, state: FSMContext):
        """Обработка выбора времени прибытия для чек-ина 2-го типа."""
        user_id = callback.from_user.id
        logger.info(f"Выбор времени прибытия: {callback.data} пользователем {user_id}")
        try:
            data = await state.get_data()
            spot_id = data.get("spot_id")
            checkin_type = data.get("checkin_type")
            if not spot_id or checkin_type != 2:
                await callback.message.edit_text("😕 Ошибка: данные не найдены, бро!")
                await state.clear()
                return
            planned_hours = int(callback.data.split(":", 1)[1])
            user = User(
                id=user_id,
                name=callback.from_user.full_name,
                username=callback.from_user.username,
            )
            success = await checkin_service.create_checkin(
                user, spot_id, checkin_type, duration=3600, planned_hours=planned_hours
            )
            if success:
                await callback.message.edit_text(
                    f"📅 План прибытия на '{data.get('spot_name')}' через {planned_hours} ч записан, бро! 🏄‍♂️"
                )
            else:
                await callback.message.edit_text(
                    f"😕 Не удалось запланировать прибытие на '{data.get('spot_name')}', бро!"
                )
            await state.clear()
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_planned_time: {e}")
            await callback.message.edit_text(
                f"😕 Ошибка при выборе времени прибытия: {str(e)}"
            )
            await state.clear()

    @dp.callback_query(lambda c: c.data and c.data.startswith("leave_spot:"))
    async def callback_leave_spot(callback: CallbackQuery, state: FSMContext):
        """Обработка кнопки 'Покинуть спот'."""
        user_id = callback.from_user.id
        logger.info(
            f"Нажата кнопка 'Покинуть спот': {callback.data} от пользователя {user_id}"
        )
        try:
            checkin_id = int(callback.data.split(":", 1)[1])
            checkin = await checkin_service.checkin_repo.get_by_id(checkin_id)
            if not checkin or not checkin.active:
                await callback.message.edit_text("😕 Чек-ин не найден или не активен, бро!")
                await state.clear()
                return
            spot = await checkin_service.spot_service.get_spot_by_id(checkin.spot_id)
            if not spot:
                await callback.message.edit_text("😕 Спот не найден, бро!")
                await state.clear()
                return
            now = datetime.utcnow()
            is_expired = checkin.active_until and checkin.active_until < now
            update_duration = not is_expired
            await checkin_service.checkin_repo.deactivate_checkin(checkin_id, update_duration=update_duration)
            user = User(
                id=user_id,
                name=callback.from_user.full_name,
                username=callback.from_user.username,
            )
            await checkin_service.notification_service.send_checkout_notification(
                user, spot.name
            )
            await checkin_service.notification_service.send_spot_checkout_notification(
                user, spot.name, checkin.type
            )
            kb = await MainKeyboards.get_main_menu(user_id, checkin_service.checkin_repo)
            await callback.message.edit_text(
                f"🚪 Йо, ты покинул '{spot.name}'! 💨 Лови главное меню! 🏄‍♂️",
                reply_markup=kb,
            )
            logger.info(
                f"Пользователь {user_id} покинул спот '{spot.name}' (чек-ин #{checkin_id})"
            )
            await state.clear()
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_leave_spot: {e}")
            await callback.message.edit_text(f"😕 Ошибка при покидании спота: {str(e)}")
            await state.clear()

    @dp.callback_query(lambda c: c.data and c.data.startswith("extend_checkin:"))
    async def callback_extend_checkin(callback: CallbackQuery, state: FSMContext):
        """Обработка кнопки 'Продлить чек-ин'."""
        user_id = callback.from_user.id
        logger.info(f"Нажата кнопка 'Продлить чек-ин': {callback.data} от пользователя {user_id}")
        try:
            checkin_id = int(callback.data.split(":", 1)[1])
            checkin = await checkin_service.checkin_repo.get_by_id(checkin_id)
            if not checkin or not checkin.active:
                await callback.message.edit_text("😕 Чек-ин не найден или не активен, бро!")
                await state.clear()
                return
            spot = await checkin_service.spot_service.get_spot_by_id(checkin.spot_id)
            if not spot:
                await callback.message.edit_text("😕 Спот не найден, бро!")
                await state.clear()
                return
            new_active_until = checkin.active_until + timedelta(hours=1)
            new_duration = checkin.duration + 3600
            success = await checkin_service.update_checkin_duration(
                checkin_id, new_active_until, new_duration
            )
            if success:
                await callback.message.edit_text(
                    f"✅ Чек-ин на '{spot.name}' продлен на 1 час! 🏄‍♂️"
                )
            else:
                await callback.message.edit_text(
                    f"😕 Не удалось продлить чек-ин на '{spot.name}', бро!"
                )
            await state.clear()
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_extend_checkin: {e}")
            await callback.message.edit_text(f"😕 Ошибка при продлении чек-ина: {str(e)}")
            await state.clear()

    @dp.callback_query(lambda c: c.data and c.data.startswith("confirm_arrival:"))
    async def callback_confirm_arrival(callback: CallbackQuery, state: FSMContext):
        """Обработка кнопки 'Я на месте' для чек-ина 2-го типа."""
        user_id = callback.from_user.id
        logger.info(f"Нажата кнопка 'Я на месте': {callback.data} от пользователя {user_id}")
        try:
            checkin_id = int(callback.data.split(":", 1)[1])
            checkin = await checkin_service.checkin_repo.get_by_id(checkin_id)
            if not checkin or checkin.type != 2 or not checkin.active:
                await callback.message.edit_text(
                    f"😕 Чек-ин не найден, не типа 2 или не активен, бро!"
                )
                await state.clear()
                return
            spot = await checkin_service.spot_service.get_spot_by_id(checkin.spot_id)
            if not spot:
                await callback.message.edit_text("😕 Спот не найден, бро!")
                await state.clear()
                return
            await state.update_data(checkin_id=checkin_id, spot_name=spot.name)
            kb = MainKeyboards.get_duration_options()
            await callback.message.edit_text(
                f"✅ Йо, ты на '{spot.name}'! Лови вайб! 🏄‍♂️\nСколько тусить будешь?",
                reply_markup=kb,
            )
            await state.set_state(CheckinStates.confirming_duration)
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_confirm_arrival: {e}")
            await callback.message.edit_text(
                f"😕 Ошибка при подтверждении прибытия: {str(e)}"
            )
            await state.clear()

    @dp.callback_query(
        lambda c: c.data and c.data.startswith("duration:"), CheckinStates.confirming_duration
    )
    async def callback_confirm_duration(callback: CallbackQuery, state: FSMContext):
        """Обработка выбора длительности при подтверждении прибытия."""
        user_id = callback.from_user.id
        logger.info(f"Выбор длительности при подтверждении: {callback.data} пользователем {user_id}")
        try:
            data = await state.get_data()
            checkin_id = data.get("checkin_id")
            spot_name = data.get("spot_name")
            if not checkin_id or not spot_name:
                await callback.message.edit_text("😕 Ошибка: данные не найдены, бро!")
                await state.clear()
                return
            duration_hours = int(callback.data.split(":", 1)[1])
            duration_seconds = duration_hours * 3600
            user = User(
                id=user_id,
                name=callback.from_user.full_name,
                username=callback.from_user.username,
            )
            success = await checkin_service.confirm_arrival(checkin_id, user, duration=duration_seconds)
            if success:
                await callback.message.edit_text(
                    f"✅ Йо, ты на '{spot_name}'! Лови волну на {duration_hours} ч! 🏄‍♂️"
                )
            else:
                await callback.message.edit_text(
                    f"😕 Не удалось подтвердить прибытие на '{spot_name}', бро!"
                )
            await state.clear()
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_confirm_duration: {e}")
            await callback.message.edit_text(
                f"😕 Ошибка при выборе длительности: {str(e)}"
            )
            await state.clear()

    @dp.callback_query(lambda c: c.data and c.data.startswith("planned_action:"))
    async def callback_planned_action(callback: CallbackQuery, state: FSMContext):
        """Обработка действий из напоминания для чек-ина типа 3."""
        user_id = callback.from_user.id
        logger.info(f"Обработка действия напоминания: {callback.data} пользователем {user_id}")
        try:
            action, checkin_id = callback.data.split(":", 1)[1].split("_")
            checkin_id = int(checkin_id)
            checkin = await checkin_service.checkin_repo.get_by_id(checkin_id)
            if not checkin or checkin.type != 3 or not checkin.active:
                await callback.message.edit_text("😕 План не найден или не активен, бро!")
                await state.clear()
                return
            spot = await checkin_service.spot_service.get_spot_by_id(checkin.spot_id)
            if not spot:
                await callback.message.edit_text("😕 Спот не найден, бро!")
                await state.clear()
                return
            user = User(
                id=user_id,
                name=callback.from_user.full_name,
                username=callback.from_user.username,
            )
            if action == "type1":
                kb = MainKeyboards.get_duration_options()
                await callback.message.edit_text(
                    f"✅ Йо, ты на '{spot.name}'! Лови вайб! 🏄‍♂️\nСколько тусить будешь?",
                    reply_markup=kb,
                )
                await state.update_data(checkin_type=1, spot_id=spot.id, spot_name=spot.name)
                await state.set_state(CheckinStates.selecting_duration)
            elif action == "type2":
                kb = MainKeyboards.get_planned_time_options()
                await callback.message.edit_text(
                    f"📅 Йо, когда планируешь быть на '{spot.name}'? 🏄‍♂️",
                    reply_markup=kb,
                )
                await state.update_data(checkin_type=2, spot_id=spot.id, spot_name=spot.name)
                await state.set_state(CheckinStates.selecting_planned_time)
            elif action == "cancel":
                success = await checkin_service.cancel_planned_checkin(checkin_id, user)
                if success:
                    await callback.message.edit_text(
                        f"❌ Планы на '{spot.name}' отменены, бро! 😎"
                    )
                else:
                    await callback.message.edit_text(
                        f"😕 Не удалось отменить планы на '{spot.name}', бро!"
                    )
            await state.clear()
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_planned_action: {e}")
            await callback.message.edit_text(f"😕 Ошибка при обработке действия: {str(e)}")
            await state.clear()

    @dp.callback_query(lambda c: c.data == "back_to_location")
    async def callback_back_to_location(callback: CallbackQuery, state: FSMContext):
        """Обработка возврата к запросу геолокации."""
        user_id = callback.from_user.id
        logger.info(f"Нажата кнопка 'Назад' от пользователя {user_id}")
        await state.clear()
        await geo_service.request_location(callback.message, state, user_id)
        await callback.message.edit_text("🤙 Йо, отправь геолокацию, бро! 📍")
        await state.set_state(CheckinStates.requesting_location)
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "back_to_spots")
    async def callback_back_to_spots(callback: CallbackQuery, state: FSMContext):
        """Обработка возврата к выбору спота."""
        user_id = callback.from_user.id
        logger.info(f"Нажата кнопка 'Назад' от пользователя {user_id}")
        data = await state.get_data()
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        if latitude and longitude:
            spots = await spot_service.get_all_spots()
            nearby_spots = await geo_service.get_nearby_spots(
                spots, latitude, longitude
            )
            if not nearby_spots:
                await callback.message.edit_text(
                    "🤙 Йо, споты не найдены! Добавь новый через /add_spot! 🪁"
                )
                await state.clear()
                return
            kb = MainKeyboards.get_spots_list(nearby_spots)
            await callback.message.edit_text(
                "🏄‍♂️ Выбери спот для чек-ина:", reply_markup=kb
            )
            await state.set_state(CheckinStates.selecting_spot)
        else:
            await callback.message.edit_text(
                "😕 Ге habitableикация не найдена. Отправь заново, бро!"
            )
            await geo_service.request_location(callback.message, state, user_id)
            await state.set_state(CheckinStates.requesting_location)
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "back_to_type")
    async def callback_back_to_type(callback: CallbackQuery, state: FSMContext):
        """Обработка возврата к выбору типа чек-ина."""
        user_id = callback.from_user.id
        logger.info(f"Нажата кнопка 'Назад' к типу чек-ина от пользователя {user_id}")
        data = await state.get_data()
        spot_name = data.get("spot_name")
        if not spot_name:
            await callback.message.edit_text("😕 Ошибка: спот не выбран, бро!")
            await state.clear()
            return
        kb = MainKeyboards.get_checkin_types()
        await callback.message.edit_text(
            f"🏄‍♂️ Йо, ты выбрал '{spot_name}'! Какой вайб? 💨", reply_markup=kb
        )
        await state.set_state(CheckinStates.selecting_type)
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "back_to_date")
    async def callback_back_to_date(callback: CallbackQuery, state: FSMContext):
        """Обработка возврата к выбору даты."""
        user_id = callback.from_user.id
        logger.info(f"Нажата кнопка 'Назад' к выбору даты от пользователя {user_id}")
        data = await state.get_data()
        spot_name = data.get("spot_name")
        if not spot_name:
            await callback.message.edit_text("😕 Ошибка: спот не выбран, бро!")
            await state.clear()
            return
        kb = MainKeyboards.get_date_options()
        await callback.message.edit_text(
            f"📅 Шаг 2/2: Выбери дату поездки на '{spot_name}':", reply_markup=kb
        )
        await state.set_state(CheckinStates.selecting_date)
        await callback.answer()

    @dp.callback_query(lambda c: c.data and c.data.startswith("cancel_checkin:"))
    async def callback_cancel_checkin(callback: CallbackQuery, state: FSMContext):
        """Обработка кнопки 'Отменить чек-ин'."""
        user_id = callback.from_user.id
        logger.info(f"Нажата кнопка 'Отменить чек-ин': {callback.data} от пользователя {user_id}")
        try:
            checkin_id = int(callback.data.split(":", 1)[1])
            user = User(
                id=user_id,
                name=callback.from_user.full_name,
                username=callback.from_user.username,
            )
            checkin = await checkin_service.checkin_repo.get_by_id(checkin_id)
            if not checkin or not checkin.active:
                await callback.message.edit_text("😕 Чек-ин не найден или не активен, бро!")
                await state.clear()
                return
            spot = await checkin_service.spot_service.get_spot_by_id(checkin.spot_id)
            if not spot:
                await callback.message.edit_text("😕 Спот не найден, бро!")
                await state.clear()
                return

            success = False
            if checkin.type == 1:
                # Деактивируем чек-ин типа 1
                now = datetime.utcnow()
                is_expired = checkin.active_until and checkin.active_until < now
                update_duration = not is_expired
                success = await checkin_service.deactivate_checkin(checkin_id, update_duration=update_duration)
            elif checkin.type == 2:
                # Удаляем чек-ин типа 2
                success = await checkin_service.delete_checkin(checkin_id, user)
            elif checkin.type == 3:
                # Отменяем плановый чек-ин типа 3
                success = await checkin_service.cancel_planned_checkin(checkin_id, user)

            if success:
                await callback.message.edit_text(
                    f"❌ Йо, ты отменил чек-ин на '{spot.name}', бро! 😎"
                )
            else:
                await callback.message.edit_text(
                    f"😕 Не удалось отменить чек-ин на '{spot.name}', бро! Попробуй еще раз."
                )
            await state.clear()
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_cancel_checkin: {e}")
            await callback.message.edit_text(
                f"😕 Ошибка при отмене чек-ина: {str(e)}"
            )
            await state.clear()

    @dp.callback_query(lambda c: c.data == "main_menu")
    async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
        """Обработка возврата в главное меню."""
        user_id = callback.from_user.id
        logger.info(f"Нажата кнопка 'В главное меню' от пользователя {user_id}")
        await state.clear()
        kb = await MainKeyboards.get_main_menu(user_id, checkin_service.checkin_repo)
        await callback.message.edit_text(
            "🤙 Йо, бро! Лови главное меню WindSpotBot! 🏄‍♂️\n"
            "Найди спот, чек-инься или туси в @WindSpotRU! 💨",
            reply_markup=kb,
        )
        await callback.answer()
