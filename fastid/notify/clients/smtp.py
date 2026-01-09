import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastid.auth.schemas import Contact


class MailClient:
    def __init__(
        self,
        client: smtplib.SMTP,
        *,
        from_name: str,
    ) -> None:
        self._client = client
        self.username = self._client.user
        self.from_name = from_name

    async def send(self, contact: Contact, subject: str, content: str) -> None:
        await asyncio.to_thread(self._send, contact, subject, content)

    def _send(self, contact: Contact, subject: str, content: str) -> None:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.username}>"
        msg["To"] = f"<{contact.recipient['email']}>"
        msg.attach(MIMEText(content, "html"))

        self._client.send_message(msg)
