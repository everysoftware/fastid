from pydantic_settings import SettingsConfigDict

from fastid.core.schemas import ENV_PREFIX, BaseSettings


class AdminSettings(BaseSettings):
    enabled: bool = True
    email: str = "admin@fastid.com"
    password: str = "admin"

    model_config = SettingsConfigDict(env_prefix=f"{ENV_PREFIX}admin_")


admin_settings = AdminSettings()
