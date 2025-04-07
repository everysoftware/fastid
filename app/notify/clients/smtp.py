import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Self

from app.notify.clients.base import NotificationClient
from app.notify.clients.schemas import Notification


class SMTPMail(NotificationClient):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        from_name: str,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_name = from_name

        self._client = smtplib.SMTP_SSL(host, port)
        self._client.login(username, password)

    async def send(self, notification: Notification) -> None:
        await asyncio.to_thread(self._send, notification)

    def _send(self, notification: Notification) -> None:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = notification.subject
        msg["From"] = f"{self.from_name} <{self.username}>"
        msg["To"] = notification.user_email
        msg.attach(MIMEText(notification.as_html(), "html"))

        self._client.send_message(msg)

    async def __aenter__(self) -> Self:
        self._client.__enter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._client.__exit__(exc_type, exc_val, exc_tb)
