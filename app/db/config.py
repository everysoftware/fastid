from pydantic_settings import SettingsConfigDict

from app.base.schemas import BaseSettings


class DBSettings(BaseSettings):
    url: str = "postgresql+asyncpg://postgres:changethis@db:5432/app"
    echo: bool = False

    model_config = SettingsConfigDict(env_prefix="db_")


db_settings = DBSettings()
