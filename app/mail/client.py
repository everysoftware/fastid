import smtplib
from email.message import Message

from app.mail.config import mail_settings


class MailClient:
    client: smtplib.SMTP_SSL

    def __init__(self) -> None:
        self.client = smtplib.SMTP_SSL(
            mail_settings.smtp_host, mail_settings.smtp_port
        )
        self.client.login(
            mail_settings.smtp_username, mail_settings.smtp_password
        )

    def send(self, message: Message) -> None:
        with self.client as session:
            session.send_message(message)
