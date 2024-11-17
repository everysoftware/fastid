from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar, Generic, Sequence

from pydantic import computed_field, Field

from app.base.models import Entity
from app.base.schemas import BaseModel


class Pagination(BaseModel):
    pass


class LimitOffset(Pagination):
    limit: int = Field(100, ge=0)
    offset: int = Field(0, ge=0)


T = TypeVar("T", bound=Entity)


@dataclass
class Page(Generic[T]):
    items: Sequence[T]

    @property
    def total(self) -> int:
        return len(self.items)

    def __bool__(self) -> bool:
        return bool(self.items)


DTO_T = TypeVar("DTO_T", bound=BaseModel)


class PageDTO(BaseModel, Generic[DTO_T]):
    items: list[DTO_T]

    @computed_field  # type: ignore
    @property
    def total(self) -> int:
        return len(self.items)
