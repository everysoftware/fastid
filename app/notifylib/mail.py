import smtplib
from email.message import Message
from typing import Annotated

from fastapi import Depends

from app.notifylib.config import notifier_settings


class MailClient:
    client: smtplib.SMTP_SSL

    def __init__(self) -> None:
        self.client = smtplib.SMTP_SSL(
            notifier_settings.smtp_host, notifier_settings.smtp_port
        )

    def send(self, message: Message) -> None:
        self.client.login(
            notifier_settings.smtp_username, notifier_settings.smtp_password
        )
        with self.client as session:
            session.send_message(message)


def get_mail() -> MailClient:
    return MailClient()


MailDep = Annotated[MailClient, Depends(get_mail)]
