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
        mail_from: str,
    ) -> None:
        self._client = client
        self.mail_from = mail_from

    async def send(self, contact: Contact, subject: str, content: str) -> None:
        await asyncio.to_thread(self._send, contact, subject, content)

    def _send(self, contact: Contact, subject: str, content: str) -> None:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.mail_from}"
        msg["To"] = f"<{contact.recipient['email']}>"
        msg.attach(MIMEText(content, "html"))

        self._client.send_message(msg)
