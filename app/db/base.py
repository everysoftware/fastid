import datetime
from enum import Enum
from typing import Any

from sqlalchemy import BigInteger, Enum as SAEnum, MetaData, Uuid, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.domain.types import UUID, naive_utc, generate_uuid

type_map = {
    int: BigInteger,
    Enum: SAEnum(Enum, native_enum=False),
    UUID: Uuid(as_uuid=False),
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

    def dump(self) -> dict[str, Any]:
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs  # noqa
        }

    def __repr__(self) -> str:
        return repr(self.dump())


class Mixin:
    pass


class IDMixin(Mixin):
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=generate_uuid,
        sort_order=-100,
    )


class AuditMixin(Mixin):
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=naive_utc, sort_order=100
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=naive_utc,
        onupdate=naive_utc,
        sort_order=101,
    )


class BaseEntityOrm(BaseOrm, IDMixin, AuditMixin):
    __abstract__ = True
