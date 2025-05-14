from pydantic_settings import SettingsConfigDict

from fastid.core.schemas import BaseSettings


class DBSettings(BaseSettings):
    url: str
    echo: bool = False

    model_config = SettingsConfigDict(env_prefix="db_")


db_settings = DBSettings()
