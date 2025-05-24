import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Self

from fastid.notify.clients.base import NotificationClient
from fastid.notify.clients.schemas import Notification


class MailClient(NotificationClient):
    def __init__(
        self,
        client: smtplib.SMTP,
        *,
        from_name: str,
    ) -> None:
        self._client = client
        self.username = self._client.user
        self.from_name = from_name

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
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass
