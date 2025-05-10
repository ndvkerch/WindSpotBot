import pytest
from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import Command
from unittest.mock import AsyncMock
from src.bot import main
from src.services.topic import TopicService


@pytest.mark.asyncio
async def test_cmd_create_topic():
    bot = AsyncMock(spec=Bot)
    dp = Dispatcher()
    message = AsyncMock(spec=Message)
    message.from_user.id = 7395203712
    message.text = "/create_topic TestSpot"

    # Mock chat member check
    bot.get_chat_member.return_value.can_manage_topics = True

    # Mock topic service
    topic_service = AsyncMock(spec=TopicService)
    topic_service.create_topic.return_value = 12345

    # Register handler
    @dp.message(Command(commands=["create_topic"]))
    async def cmd_create_topic(message: Message):
        from src.bot import settings

        user_id = message.from_user.id
        try:
            chat_member = await bot.get_chat_member(settings.CHAT_ID, bot.id)
            if not chat_member.can_manage_topics:
                await message.answer(
                    "Бот не имеет прав для создания тем. Дайте права администратора с 'Управление темами'."
                )
                return
            spot_name = (
                message.text.split(maxsplit=1)[1]
                if len(message.text.split()) > 1
                else "Тест"
            )
            thread_id = await topic_service.create_topic(spot_name)
            if thread_id:
                await message.answer(
                    f"Тема '{spot_name}' создана, thread_id: {thread_id}"
                )
            else:
                await message.answer(f"Ошибка при создании темы '{spot_name}'")
        except Exception as e:
            await message.answer(f"Не удалось создать тему: {str(e)}")

    # Feed update
    await dp.feed_update(bot=bot, update={"message": message})

    # Assertions
    message.answer.assert_called_with("Тема 'TestSpot' создана, thread_id: 12345")
