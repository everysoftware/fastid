from typing import Any

from pydantic import Field, PositiveInt
from pydantic_settings import SettingsConfigDict

from fastid.core.schemas import ENV_PREFIX, BaseSettings


class DBSettings(BaseSettings):
    url: str
    echo: bool = False

    # --- pool settings ---
    pool_size: PositiveInt = Field(default=20)
    max_overflow: int = Field(default=40, ge=0)
    pool_recycle: int = Field(default=3600, ge=0)
    pool_timeout: int = Field(default=30, ge=0)
    pool_pre_ping: bool = Field(default=True)

    # --- connect_args (asyncpg) ---
    server_settings: dict[str, Any] = Field(default_factory=lambda: {"application_name": "fastid", "timezone": "UTC"})

    # --- asyncpg timeouts ---
    connect_timeout: PositiveInt | None = Field(default=10)
    command_timeout: PositiveInt | None = Field(default=60)

    model_config = SettingsConfigDict(env_prefix=f"{ENV_PREFIX}db_")


db_settings = DBSettings()
