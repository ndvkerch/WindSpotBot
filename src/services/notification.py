from aiogram import Bot
from src.models.user import User
from src.services.topic import TopicService
from src.repositories.subscription import SubscriptionRepository
from src.config.config import settings
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис для отправки уведомлений."""

    def __init__(
        self,
        bot: Bot,
        topic_service: TopicService,
        subscription_repo: SubscriptionRepository,
    ):
        self.bot = bot
        self.topic_service = topic_service
        self.subscription_repo = subscription_repo

    async def send_checkin_notification(self, user: User, spot_name: str):
        """Отправка уведомления о чек-ине подписчикам."""
        try:
            subscribers = await self.subscription_repo.get_subscribers(
                spot_name, "checkin"
            )
            logger.info(
                f"Найдено {len(subscribers)} подписчиков для чек-ина на '{spot_name}'"
            )
            for user_id in subscribers:
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=(
                            f"🔔 Йо, <a href='tg://user?id={user.id}'>@{user.username or user.name}</a> "
                            f"зачекинился на '{spot_name}'! Лови волну? 🤙"
                        ),
                        parse_mode="HTML",
                    )
                except Exception as e:
                    logger.error(
                        f"Ошибка при отправке уведомления пользователю {user_id}: {e}"
                    )
            logger.info(
                f"Уведомления о чек-ине для '{spot_name}' отправлены {len(subscribers)} подписчикам"
            )
        except Exception as e:
            logger.error(
                f"Ошибка при обработке подписчиков для чек-ина '{spot_name}': {e}"
            )

    async def send_checkout_notification(self, user: User, spot_name: str):
        """Отправка уведомления о расчек-ине."""
        try:
            subscribers = await self.subscription_repo.get_subscribers(
                spot_name, "checkin"
            )
            logger.info(
                f"Найдено {len(subscribers)} подписчиков для расчек-ина на '{spot_name}'"
            )
            for user_id in subscribers:
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=(
                            f"🔔 Йо, <a href='tg://user?id={user.id}'>@{user.username or user.name}</a> "
                            f"покинул '{spot_name}'! 💨"
                        ),
                        parse_mode="HTML",
                    )
                except Exception as e:
                    logger.error(
                        f"Ошибка при отправке уведомления пользователю {user_id}: {e}"
                    )
            logger.info(
                f"Уведомления о расчек-ине для '{spot_name}' отправлены {len(subscribers)} подписчикам"
            )
        except Exception as e:
            logger.error(
                f"Ошибка при обработке подписчиков для расчек-ина '{spot_name}': {e}"
            )

    async def send_message_notification(
        self, spot_name: str, message_text: str, sender: User
    ):
        """Отправка уведомления о новом сообщении в чате."""
        try:
            subscribers = await self.subscription_repo.get_subscribers(
                spot_name, "message"
            )
            logger.info(
                f"Найдено {len(subscribers)} подписчиков для сообщения на '{spot_name}'"
            )
            for user_id in subscribers:
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=(
                            f"🪁 Новое сообщение в чате '{spot_name}' от "
                            f"<a href='tg://user?id={sender.id}'>@{sender.username or sender.name}</a>: "
                            f"{message_text[:100]}... 🤙"
                        ),
                        parse_mode="HTML",
                    )
                except Exception as e:
                    logger.error(
                        f"Ошибка при отправке уведомления пользователю {user_id}: {e}"
                    )
            logger.info(
                f"Уведомления о сообщении для '{spot_name}' отправлены {len(subscribers)} подписчикам"
            )
        except Exception as e:
            logger.error(
                f"Ошибка при обработке подписчиков для сообщения '{spot_name}': {e}"
            )

    async def send_weather_notification(self, spot_name: str, weather_data: dict):
        """Отправка уведомления об изменении ветра."""
        try:
            subscribers = await self.subscription_repo.get_subscribers(
                spot_name, "weather"
            )
            logger.info(
                f"Найдено {len(subscribers)} подписчиков для погоды на '{spot_name}'"
            )
            wind_speed = weather_data.get("wind_speed", "N/A")
            for user_id in subscribers:
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=f"💨 Ветер на споте '{spot_name}' изменился: {wind_speed} м/с! 🏄‍♂️",
                        parse_mode="HTML",
                    )
                except Exception as e:
                    logger.error(
                        f"Ошибка при отправке уведомления пользователю {user_id}: {e}"
                    )
            logger.info(
                f"Уведомления о погоде для '{spot_name}' отправлены {len(subscribers)} подписчикам"
            )
        except Exception as e:
            logger.error(
                f"Ошибка при обработке подписчиков для погоды '{spot_name}': {e}"
            )

    async def send_spot_checkin_notification(self, user: User, spot_name: str):
        """Отправка уведомления о чек-ине в тему спота."""
        try:
            thread_id = await self.topic_service.get_topic_id(spot_name)
            logger.info(
                f"Отправка уведомления в тему '{spot_name}', thread_id={thread_id}, chat_id={settings.CHAT_ID}"
            )
            if thread_id:
                await self.bot.send_message(
                    chat_id=settings.CHAT_ID,
                    message_thread_id=thread_id,
                    text=(
                        f"🪁 <a href='tg://user?id={user.id}'>@{user.username or user.name}</a> "
                        f"зачекинился на #{spot_name}: Ветер огонь! 🤙"
                    ),
                    parse_mode="HTML",
                )
                logger.info(f"Уведомление о чек-ине отправлено в тему #{spot_name}")
            else:
                logger.warning(f"Тема для спота '{spot_name}' не найдена")
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления в тему '{spot_name}': {e}")

    async def send_spot_checkout_notification(self, user: User, spot_name: str):
        """Отправка уведомления о расчек-ине в тему спота."""
        try:
            thread_id = await self.topic_service.get_topic_id(spot_name)
            logger.info(
                f"Отправка уведомления о расчек-ине в тему '{spot_name}', thread_id={thread_id}, chat_id={settings.CHAT_ID}"
            )
            if thread_id:
                await self.bot.send_message(
                    chat_id=settings.CHAT_ID,
                    message_thread_id=thread_id,
                    text=(
                        f"🚪 <a href='tg://user?id={user.id}'>@{user.username or user.name}</a> "
                        f"покинул #{spot_name}. 💨"
                    ),
                    parse_mode="HTML",
                )
                logger.info(f"Уведомление о расчек-ине отправлено в тему #{spot_name}")
            else:
                logger.warning(f"Тема для спота '{spot_name}' не найдена")
        except Exception as e:
            logger.error(
                f"Ошибка при отправке уведомления о расчек-ине в тему '{spot_name}': {e}"
            )
