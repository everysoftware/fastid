from app.domain.schemas import BaseSettings


class DBSettings(BaseSettings):
    db_url: str = "postgresql+asyncpg://postgres:changethis@db:5432/app"
    db_echo: bool = False
