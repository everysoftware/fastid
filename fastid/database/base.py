import datetime
from enum import Enum
from typing import Any, Self
from uuid import UUID

from sqlalchemy import BigInteger, MetaData, Uuid, inspect
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

from fastid.core.schemas import BaseModel
from fastid.database.utils import naive_utc, uuid

type_map = {
    int: BigInteger,
    Enum: SAEnum(Enum, native_enum=False),
    UUID: Uuid(),
}

NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(naming_convention=NAMING_CONVENTION)


class BaseOrm(DeclarativeBase):
    type_annotation_map = type_map
    metadata = metadata

    @classmethod
    def from_dto(cls, model: BaseModel) -> Self:
        return cls(**model.model_dump())

    def dump(self) -> dict[str, Any]:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def merge_model(self, model: BaseModel) -> Self:
        for key, value in model.model_dump(exclude_unset=True).items():
            setattr(self, key, value)
        return self

    def merge_attrs(self, **attrs: Any) -> Self:
        for key, value in attrs.items():
            setattr(self, key, value)
        return self

    def __repr__(self) -> str:
        return repr(self.dump())


class Mixin:
    pass


class UUIDMixin(Mixin):
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid,
        sort_order=-100,
    )


class AuditMixin(Mixin):
    created_at: Mapped[datetime.datetime] = mapped_column(default=naive_utc, sort_order=100)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=naive_utc,
        onupdate=naive_utc,
        sort_order=101,
    )


class Entity(BaseOrm, UUIDMixin, AuditMixin):
    __abstract__ = True
