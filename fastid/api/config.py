from collections.abc import Sequence

from fastid.core.schemas import BaseSettings


class APISettings(BaseSettings):
    cors_origins: Sequence[str] = ("*",)
    cors_origin_regex: str | None = None


api_settings = APISettings()
