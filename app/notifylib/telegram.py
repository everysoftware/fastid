from typing import Annotated, AsyncGenerator

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from fastapi import Depends

from app.oauth.config import telegram_settings


async def get_bot() -> AsyncGenerator[Bot, None]:
    async with Bot(
        telegram_settings.bot_token,
        default=DefaultBotProperties(),
    ) as bot:
        yield bot


BotDep = Annotated[Bot, Depends(get_bot)]
