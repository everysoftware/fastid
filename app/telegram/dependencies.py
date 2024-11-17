from typing import Annotated, AsyncGenerator

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from fastapi import Depends

from app.oauthlib.config import telegram_settings


async def get_bot() -> AsyncGenerator[Bot, None]:
    async with Bot(
        telegram_settings.client_secret,
        default=DefaultBotProperties(),
    ) as bot:
        yield bot


BotDep = Annotated[Bot, Depends(get_bot)]
