from __future__ import annotations

from typing import TypeVar, Generic

from pydantic import computed_field, Field

from app.domain.schemas import BaseModel


class Pagination(BaseModel):
    pass


class LimitOffset(Pagination):
    limit: int = Field(100, ge=0)
    offset: int = Field(0, ge=0)


T = TypeVar("T", bound=BaseModel)


class Page(BaseModel, Generic[T]):
    items: list[T]

    @computed_field  # type: ignore
    @property
    def total(self) -> int:
        return len(self.items)

    def __bool__(self) -> bool:
        return bool(self.items)
