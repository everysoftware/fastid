from pydantic import Field

from fastid.core.config import branding_settings
from fastid.core.schemas import BaseSettings


class EmailSettings(BaseSettings):
    smtp_enabled: bool = False
    smtp_ssl: bool = False
    smtp_host: str = "mailpit"
    smtp_port: int = 1025
    smtp_auth: bool = False
    smtp_username: str = "user@example.com"
    smtp_password: str = "password"
    smtp_from_email: str = Field(default_factory=lambda data: data["smtp_username"])

    @property
    def smtp_from(self) -> str:
        return f"{branding_settings.notify_from} <{self.smtp_from_email}>"


email_settings = EmailSettings()
