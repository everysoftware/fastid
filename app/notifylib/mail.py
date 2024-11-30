import smtplib
from email.message import Message
from functools import cached_property
from typing import Annotated

from fastapi import Depends

from app.notifylib.config import notifier_settings


class MailClient:
    _client: smtplib.SMTP_SSL | None

    def __init__(self) -> None:
        self._client = None

    @cached_property
    def client(self) -> smtplib.SMTP_SSL:
        if self._client is None:
            self._client = smtplib.SMTP_SSL(
                notifier_settings.smtp_host, notifier_settings.smtp_port
            )
        return self._client

    def send(self, message: Message) -> None:
        self.client.login(
            notifier_settings.smtp_username, notifier_settings.smtp_password
        )
        with self.client as session:
            session.send_message(message)


def get_mail() -> MailClient:
    return MailClient()


MailDep = Annotated[MailClient, Depends(get_mail)]
