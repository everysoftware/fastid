from app.domain.schemas import BaseSettings


class MailSettings(BaseSettings):
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_name: str = "FastAPI"
