from __future__ import annotations

import datetime
from typing import Self, Final, overload, Literal

from pydantic import BaseModel as PydanticBaseModel, ConfigDict, Field
from pydantic_settings import (
    BaseSettings as PydanticBaseSettings,
    SettingsConfigDict,
)

from app.base.types import UUID, naive_utc, uuid


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(use_enum_values=True)


# Domain models
class EntityDTO(BaseModel):
    id: UUID = Field(default_factory=uuid)
    created_at: datetime.datetime = Field(default_factory=naive_utc)
    updated_at: datetime.datetime = Field(default_factory=naive_utc)

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    @overload
    def from_model[T](cls, model: T) -> Self: ...

    @classmethod
    @overload
    def from_model[T](cls, model: Literal[None] = None) -> Self | None: ...

    @classmethod
    def from_model[T](cls, model: T | None = None) -> Self | None:
        if model is None:
            return None
        return cls.model_validate(model)


class ErrorResponse(BaseModel):
    msg: str
    type: str


OK: Final = ErrorResponse(msg="ok", type="ok")
INTERNAL_ERR: Final = ErrorResponse(
    msg="Internal Server Error", type="unexpected_error"
)


# Settings
class BaseSettings(PydanticBaseSettings):
    model_config = SettingsConfigDict(extra="allow", env_file=".env")
