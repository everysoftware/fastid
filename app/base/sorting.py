from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Self, cast

from app.api.exceptions import ValidationError
from app.base.models import Entity
from app.base.schemas import BaseModel


@dataclass
class SortingEntry:
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
        if order not in ["asc", "desc"]:
            raise ValidationError(f"Invalid sorting order: {order}")
        if not hasattr(model_type, field):
            raise ValidationError(f"Invalid sorting field: {field}")
        return cls(field, cast(Literal["asc", "desc"], order))


class Sorting(BaseModel):
    sort: str = "updated_at:desc"

    def render(self, model_type: type[Entity]) -> Sequence[SortingEntry]:
        sort = self.sort.split(",")
        return [SortingEntry.from_str(model_type, value) for value in sort]
