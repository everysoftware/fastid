from typing import Annotated, Any, Self

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from fastapi import Depends

from app.notify.base import Notification
from app.oauth.config import telegram_settings


class TelegramAdapter:
    def __init__(self, bot_token: str) -> None:
        self._bot = Bot(bot_token, default=DefaultBotProperties(parse_mode="Markdown"))

    async def send(self, notification: Notification) -> None:
        await self._bot.send_message(notification.user_telegram_id, notification.as_markdown())

    async def __aenter__(self) -> Self:
        await self._bot.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self._bot.__aexit__(exc_type, exc_val, exc_tb)


def get_telegram() -> TelegramAdapter:
    return TelegramAdapter(
        telegram_settings.bot_token,
    )


TelegramDep = Annotated[TelegramAdapter, Depends(get_telegram)]
