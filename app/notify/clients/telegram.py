from typing import Any, Self

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from app.notify.clients.base import NotificationClient
from app.notify.clients.schemas import Notification


class TelegramAdapter(NotificationClient):
    def __init__(self, bot_token: str) -> None:
        self._bot = Bot(bot_token, default=DefaultBotProperties(parse_mode="Markdown"))

    async def send(self, notification: Notification) -> None:
        await self._bot.send_message(notification.user_telegram_id, notification.as_markdown())

    async def __aenter__(self) -> Self:
        await self._bot.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self._bot.__aexit__(exc_type, exc_val, exc_tb)
