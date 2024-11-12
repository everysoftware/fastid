from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast, Sequence

from app.domain.schemas import BaseModel


@dataclass
class SortEntry:
    field: str
    order: Literal["asc", "desc"] = "asc"

    @classmethod
    def from_str(cls, value: str) -> SortEntry:
        values = value.lower().split(":")
        if len(values) == 1:
            return SortEntry(values[0])
        if len(values) == 2 and values[1] in ["asc", "desc"]:
            return SortEntry(
                values[0], cast(Literal["asc", "desc"], values[1])
            )
        raise ValueError(f"Invalid sorting: {value}")


class Sorting(BaseModel):
    sort: str = "updated_at:desc"

    def entries(self) -> Sequence[SortEntry]:
        sort = self.sort.split(",")
        return [SortEntry.from_str(value) for value in sort]
