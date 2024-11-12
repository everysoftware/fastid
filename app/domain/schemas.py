from __future__ import annotations

import datetime
from typing import Self, Final, Any

from pydantic import BaseModel as PydanticBaseModel, ConfigDict, Field
from pydantic_settings import (
    BaseSettings as PydanticBaseSettings,
    SettingsConfigDict,
)

from app.domain.types import UUID, naive_utc, generate_uuid


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict()

    @classmethod
    def from_model(cls, model: BaseModel) -> Self:
        return cls.model_validate(model, from_attributes=True)

    def merge_model(self, model: BaseModel) -> Self:
        for key, value in model.model_dump(exclude_unset=True).items():
            setattr(self, key, value)
        return self

    def merge_attrs(self, **attrs: Any) -> Self:
        for key, value in attrs.items():
            setattr(self, key, value)
        return self


# Domain models
class DomainModel(BaseModel):
    id: UUID = Field(default_factory=generate_uuid)
    created_at: datetime.datetime = Field(default_factory=naive_utc)
    updated_at: datetime.datetime = Field(default_factory=naive_utc)

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class ErrorResponse(BaseModel):
    msg: str
    code: str


OK: Final = ErrorResponse(msg="ok", code="ok")
INTERNAL_ERR: Final = ErrorResponse(
    msg="Internal Server Error", code="unexpected_error"
)


# Settings
class BaseSettings(PydanticBaseSettings):
    model_config = SettingsConfigDict(extra="allow")
