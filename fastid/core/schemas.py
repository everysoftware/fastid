from __future__ import annotations

from enum import StrEnum
from typing import Final

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict

ENV_FILE = ".env"
ENV_PREFIX = "fastid_"


class BaseEnum(StrEnum):
    pass


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(use_enum_values=True)


class BaseSettings(PydanticBaseSettings):
    model_config = SettingsConfigDict(extra="allow", env_file=ENV_FILE, env_prefix=ENV_PREFIX)


class ErrorResponse(BaseModel):
    msg: str
    type: str


OK: Final = ErrorResponse(msg="ok", type="ok")
INTERNAL_ERR: Final = ErrorResponse(msg="Internal Server Error", type="unexpected_error")
