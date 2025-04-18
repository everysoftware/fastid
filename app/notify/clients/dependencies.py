from typing import Annotated

from fastapi import Depends

from app.notify.clients.smtp import SMTPMail
from app.notify.clients.telegram import TelegramAdapter
from app.notify.config import notify_settings
from app.oauth.config import telegram_settings


def get_mail() -> SMTPMail:
    return SMTPMail(
        notify_settings.smtp_host,
        notify_settings.smtp_port,
        notify_settings.smtp_username,
        notify_settings.smtp_password,
        notify_settings.from_name,
    )


def get_telegram() -> TelegramAdapter:
    return TelegramAdapter(
        telegram_settings.bot_token,
    )


MailDep = Annotated[SMTPMail, Depends(get_mail)]
TelegramDep = Annotated[TelegramAdapter, Depends(get_telegram)]
