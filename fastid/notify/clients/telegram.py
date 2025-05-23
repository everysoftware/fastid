from typing import Any, Self

from aiogram import Bot

from fastid.notify.clients.base import NotificationClient
from fastid.notify.clients.schemas import Notification


class TelegramNotificationClient(NotificationClient):
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def send(self, notification: Notification) -> None:
        await self._bot.send_message(notification.user_telegram_id, notification.as_markdown())

    async def __aenter__(self) -> Self:
        await self._bot.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self._bot.__aexit__(exc_type, exc_val, exc_tb)
