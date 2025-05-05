from __future__ import annotations

import datetime  # noqa: TCH003
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Literal, Self, TypeVar, cast

from pydantic import ConfigDict, Field, computed_field

from fastid.api.exceptions import ValidationError
from fastid.core.schemas import BaseModel
from fastid.database.base import Entity
from fastid.database.utils import UUIDv7, naive_utc, uuid

if TYPE_CHECKING:
    from collections.abc import Sequence

T = TypeVar("T", bound=Entity)
DTO_T = TypeVar("DTO_T", bound=BaseModel)


class EntityDTO(BaseModel):
    id: UUIDv7 = Field(default_factory=uuid)
    created_at: datetime.datetime = Field(default_factory=naive_utc)
    updated_at: datetime.datetime = Field(default_factory=naive_utc)

    model_config = ConfigDict(from_attributes=True)


@dataclass
class SortingElement:
    field: str
    order: Literal["asc", "desc"] = "asc"

    @classmethod
    def from_str(cls, model_type: type[Entity], value: str) -> Self:
        values = value.lower().split(":")
        match len(values):
            case 1:
                field, order = values[0], "asc"
            case 2:
                field, order = values
            case _:
                raise ValidationError(f"Invalid format: {value}")
        if order not in {"asc", "desc"}:
            raise ValidationError(f"Invalid sorting order: {order}")
        if not hasattr(model_type, field):
            raise ValidationError(f"Invalid sorting field: {field}")
        return cls(field, cast(Literal["asc", "desc"], order))


class Sorting(BaseModel):
    sort: str = "updated_at:desc"

    def render(self, model_type: type[Entity]) -> Sequence[SortingElement]:
        sort = self.sort.split(",")
        return [SortingElement.from_str(model_type, value) for value in sort]


class Pagination(BaseModel):
    pass


class LimitOffset(Pagination):
    limit: int = Field(100, ge=0)
    offset: int = Field(0, ge=0)


@dataclass
class Page(Generic[T]):
    items: Sequence[T]

    @property
    def total(self) -> int:
        return len(self.items)


class PageDTO(BaseModel, Generic[DTO_T]):
    items: list[DTO_T]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total(self) -> int:
        return len(self.items)
