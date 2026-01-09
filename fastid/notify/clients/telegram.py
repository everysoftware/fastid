from typing import Any, Self

from aiogram import Bot

from fastid.auth.schemas import Contact


class TelegramNotificationClient:
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def send(self, contact: Contact, content: str) -> None:
        async with self._bot:
            await self._bot.send_message(contact.recipient["telegram_id"], content)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass
