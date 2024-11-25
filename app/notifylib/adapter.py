import asyncio
from abc import ABC, abstractmethod

from app.notifylib.base import Notification
from app.notifylib.mail import MailDep
from app.notifylib.telegram import BotDep


class INotifier(ABC):
    @abstractmethod
    async def push(self, notification: Notification) -> None: ...


class Notifier(INotifier):
    def __init__(self, mail: MailDep, bot: BotDep) -> None:
        self.mail = mail
        self.bot = bot

    async def push(self, notification: Notification) -> None:
        method: str
        if notification.method == "auto":
            method = notification.user.available_contact
        else:
            method = notification.method
        match method:
            case "email":
                await asyncio.to_thread(
                    self.mail.send, notification.as_email()
                )
            case "telegram":
                await self.bot.send_message(**notification.as_telegram())
            case _:
                raise ValueError(f"Unknown method: {method}")
