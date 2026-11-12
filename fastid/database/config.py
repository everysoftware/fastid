from typing import Any, Self

from pydantic import AliasChoices, Field, PositiveInt, field_validator, model_validator
from pydantic_settings import SettingsConfigDict

from fastid.core.schemas import ENV_PREFIX, BaseSettings


class DBSettings(BaseSettings):
    url: str = Field(
        validation_alias=AliasChoices(
            f"{ENV_PREFIX}db_url",
            f"{ENV_PREFIX}test_db_url",
        ),
    )
    echo: bool = False

    # --- pool settings ---
    pool_size: PositiveInt = Field(default=20)
    max_overflow: int = Field(default=0, ge=0)
    connection_budget: PositiveInt = 100
    workers: PositiveInt = Field(
        default=1,
        validation_alias=AliasChoices("fastid_db_workers", "fastid_gunicorn_workers", "workers"),
    )
    pool_recycle: int = Field(default=3600, ge=0)
    pool_timeout: int = Field(default=30, ge=0)
    pool_pre_ping: bool = Field(default=True)

    # --- connect_args (asyncpg) ---
    server_settings: dict[str, Any] = Field(default_factory=lambda: {"application_name": "fastid", "timezone": "UTC"})

    # --- asyncpg timeouts ---
    connect_timeout: PositiveInt | None = Field(default=10)
    command_timeout: PositiveInt | None = Field(default=60)

    @field_validator("workers", mode="before")
    @classmethod
    def default_empty_workers(cls, value: Any) -> Any:
        # Compose leaves this blank when the entrypoint will resolve it.
        return 1 if value == "" else value

    @model_validator(mode="after")
    def validate_budget(self) -> Self:
        if self.connection_budget < self.workers:
            msg = "Connection budget must allow at least one connection per worker"
            raise ValueError(msg)
        return self

    @property
    def pool_limits(self) -> tuple[int, int]:
        per_worker = self.connection_budget // self.workers
        size = min(self.pool_size, per_worker)
        return size, min(self.max_overflow, per_worker - size)

    model_config = SettingsConfigDict(env_prefix=f"{ENV_PREFIX}db_")


db_settings = DBSettings()
