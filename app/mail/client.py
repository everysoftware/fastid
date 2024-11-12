import smtplib
from email.message import Message

from app.runner.config import settings


class MailClient:
    client: smtplib.SMTP_SSL

    def __init__(self) -> None:
        self.client = smtplib.SMTP_SSL(
            settings.mail.smtp_host, settings.mail.smtp_port
        )
        self.client.login(
            settings.mail.smtp_username, settings.mail.smtp_password
        )

    def send(self, message: Message) -> None:
        with self.client as session:
            session.send_message(message)
