import logging
from aiogram import Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from src.services.checkin import CheckinService
from src.repositories.user import UserRepository
from src.keyboards.main import MainKeyboards
from src.models.user import User
from time import time

logger = logging.getLogger(__name__)

def register_plans_handlers(dp: Dispatcher):
    """Регистрация обработчиков для управления запланированными чек-инами."""
    logger.info("Регистрация обработчиков plans.py")

    @dp.callback_query(lambda c: c.data in ["plan", "refresh_plan"] or c.data.startswith("refresh_plan:"))
    async def callback_plan(callback: CallbackQuery, state: FSMContext, checkin_service: CheckinService, user_repo: UserRepository):
        """Обработка нажатия кнопки 'Планирование' или 'Обновить'."""
        user_id = callback.from_user.id
        logger.info(f"Callback 'plan' или 'refresh_plan' от пользователя {user_id}")
        await state.clear()

        # Получаем личные запланированные чек-ины пользователя
        planned_checkins = await checkin_service.get_planned_checkins_by_user(user_id)
        logger.info(f"Найдено {len(planned_checkins)} планов для пользователя {user_id}")

        # Формируем сообщение и клавиатуру
        timestamp = int(time())  # Уникальный идентификатор для кнопки "Обновить"
        if not planned_checkins:
            message = "📅 Пока планов нет, бро! 😕\nСоздай новый через /checkin! 🏄‍♂️"
            kb = MainKeyboards.get_empty_plans_menu()
            # Обновляем callback_data кнопки "Обновить" с временной меткой
            kb.inline_keyboard[0][0].callback_data = f"refresh_plan:{timestamp}"
        else:
            message = "📅 Твои планы:\n"
            for i, checkin in enumerate(planned_checkins, 1):
                spot = await checkin_service.spot_service.get_spot_by_id(checkin.spot_id)
                if not spot:
                    logger.error(f"Спот с ID {checkin.spot_id} не найден для чек-ина {checkin.id}")
                    continue
                date_str = checkin.planned_date.strftime("%d.%m.%Y") if checkin.planned_date else "Не указана"
                message += f"{i}. {date_str}, {spot.name}\n"
            kb = MainKeyboards.get_plans_menu([checkin.id for checkin in planned_checkins])
            # Обновляем callback_data кнопки "Обновить" с временной меткой
            for row in kb.inline_keyboard:
                for button in row:
                    if button.text == "🔄 Обновить":
                        button.callback_data = f"refresh_plan:{timestamp}"

        # Проверяем, изменилось ли сообщение
        current_text = callback.message.text or ""
        current_reply_markup = callback.message.reply_markup
        if current_text != message or current_reply_markup != kb:
            try:
                await callback.message.edit_text(message, reply_markup=kb, parse_mode="HTML")
                logger.info(f"Сообщение с планами отправлено пользователю {user_id}")
            except Exception as e:
                logger.error(f"Ошибка при обновлении сообщения в callback_plan: {e}")
                await callback.message.answer(
                    "😕 Не удалось обновить планы, попробуй ещё раз!",
                    reply_markup=kb
                )
        else:
            logger.debug(f"Сообщение не изменилось, пропускаем edit_text для пользователя {user_id}")

        await callback.answer()

    @dp.callback_query(lambda c: c.data and c.data.startswith("cancel_plan:"))
    async def callback_cancel_plan(callback: CallbackQuery, state: FSMContext, checkin_service: CheckinService, user_repo: UserRepository):
        """Обработка кнопки 'Отменить план' в меню планирования."""
        user_id = callback.from_user.id
        logger.info(f"Нажата кнопка 'Отменить план': {callback.data} от пользователя {user_id}")
        try:
            checkin_id = int(callback.data.split(":", 1)[1])
            logger.debug(f"Попытка отменить чек-ин #{checkin_id}")
            checkin = await checkin_service.checkin_repo.get_by_id(checkin_id)
            if not checkin or checkin.type != 3 or not checkin.active:
                logger.warning(f"Чек-ин #{checkin_id} не найден, не типа 3 или не активен")
                await callback.message.edit_text("😕 План не найден или не активен, бро!")
                await state.clear()
                return
            spot = await checkin_service.spot_service.get_spot_by_id(checkin.spot_id)
            if not spot:
                logger.warning(f"Спот с ID {checkin.spot_id} не найден")
                await callback.message.edit_text("😕 Спот не найден, бро!")
                await state.clear()
                return
            user = User(
                id=user_id,
                name=callback.from_user.full_name,
                username=callback.from_user.username,
            )
            success = await checkin_service.cancel_planned_checkin(checkin_id, user)
            if success:
                await checkin_service.notification_service.send_spot_checkout_notification(
                    user, spot.name, checkin.type
                )
                # Показываем сообщение об отмене
                await callback.message.edit_text(
                    f"❌ Планы на '{spot.name}' отменены, бро! 😎",
                    reply_markup=None  # Временно убираем клавиатуру
                )
                logger.info(f"Чек-ин #{checkin_id} успешно отменён для пользователя {user_id}")
                # Обновляем меню планирования
                planned_checkins = await checkin_service.get_planned_checkins_by_user(user_id)
                logger.info(f"Найдено {len(planned_checkins)} планов после отмены для пользователя {user_id}")
                timestamp = int(time())  # Уникальный идентификатор для кнопки "Обновить"
                if not planned_checkins:
                    message = "📅 Пока планов нет, бро! 😕\nСоздай новый через /checkin! 🏄‍♂️"
                    kb = MainKeyboards.get_empty_plans_menu()
                    kb.inline_keyboard[0][0].callback_data = f"refresh_plan:{timestamp}"
                else:
                    message = "📅 Твои планы:\n"
                    for i, checkin in enumerate(planned_checkins, 1):
                        spot = await checkin_service.spot_service.get_spot_by_id(checkin.spot_id)
                        if not spot:
                            logger.error(f"Спот с ID {checkin.spot_id} не найден для чек-ина {checkin.id}")
                            continue
                        date_str = checkin.planned_date.strftime("%d.%m.%Y") if checkin.planned_date else "Не указана"
                        message += f"{i}. {date_str}, {spot.name}\n"
                    kb = MainKeyboards.get_plans_menu([checkin.id for checkin in planned_checkins])
                    for row in kb.inline_keyboard:
                        for button in row:
                            if button.text == "🔄 Обновить":
                                button.callback_data = f"refresh_plan:{timestamp}"
                try:
                    await callback.message.edit_text(message, reply_markup=kb, parse_mode="HTML")
                    logger.info(f"Меню планирования обновлено для пользователя {user_id}")
                except Exception as e:
                    logger.error(f"Ошибка при обновлении меню планирования: {e}")
                    await callback.message.answer(
                        "😕 Не удалось обновить планы, попробуй ещё раз!",
                        reply_markup=kb
                    )
            else:
                await callback.message.edit_text(
                    f"😕 Не удалось отменить планы на '{spot.name}', бро!"
                )
                logger.warning(f"Не удалось отменить чек-ин #{checkin_id}")
            await state.clear()
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в callback_cancel_plan для чек-ин #{checkin_id}: {e}", exc_info=True)
            await callback.message.edit_text(f"😕 Ошибка при отмене плана: {str(e)}")
            await state.clear()
