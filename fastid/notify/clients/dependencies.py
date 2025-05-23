import smtplib
from collections.abc import AsyncIterator
from typing import Annotated

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from fastapi import Depends

from fastid.notify.clients.smtp import MailClient
from fastid.notify.clients.telegram import TelegramNotificationClient
from fastid.notify.config import notify_settings
from fastid.oauth.config import telegram_settings


def get_smtp() -> smtplib.SMTP:
    server = smtplib.SMTP_SSL(notify_settings.smtp_host, notify_settings.smtp_port)
    server.login(notify_settings.smtp_username, notify_settings.smtp_password)
    return server


async def get_mail(server: Annotated[smtplib.SMTP, Depends(get_smtp)]) -> AsyncIterator[MailClient]:
    async with MailClient(
        server,
        from_name=notify_settings.from_name,
    ) as mail:
        yield mail


def get_bot() -> Bot:
    return Bot(telegram_settings.bot_token, default=DefaultBotProperties(parse_mode="Markdown"))


async def get_telegram_nc(bot: Annotated[Bot, Depends(get_bot)]) -> AsyncIterator[TelegramNotificationClient]:
    async with TelegramNotificationClient(bot) as telegram:
        yield telegram


MailDep = Annotated[MailClient, Depends(get_mail)]
TelegramDep = Annotated[TelegramNotificationClient, Depends(get_telegram_nc)]
