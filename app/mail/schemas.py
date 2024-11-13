from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from jinja2 import Environment, FileSystemLoader

from app.auth.schemas import UserDTO
from app.base.schemas import BaseModel
from app.mail.config import mail_settings

env = Environment(loader=FileSystemLoader("templates/mail"))


class MailMessage(BaseModel):
    subject: str
    template: str
    user: UserDTO

    def as_email(self, **kwargs: Any) -> Message:
        html = env.get_template(f"{self.template}.html").render(
            user=self.user, **kwargs
        )
        msg = MIMEMultipart("alternative")
        msg["From"] = mail_settings.smtp_from_name
        assert self.user.email is not None
        msg["To"] = self.user.email
        msg["Subject"] = self.subject
        msg.attach(MIMEText(html, "html"))
        return msg
