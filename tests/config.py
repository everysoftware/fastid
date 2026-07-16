from pydantic_settings import SettingsConfigDict

from fastid.core.schemas import ENV_FILE, ENV_PREFIX, BaseSettings


class TestSettings(BaseSettings):
    db_url: str
    redis_url: str

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=ENV_FILE,
        env_prefix=f"{ENV_PREFIX}test_",
    )


test_settings = TestSettings()
