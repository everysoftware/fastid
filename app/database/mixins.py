import datetime
import uuid

from sqlalchemy import func, Identity
from sqlalchemy.orm import mapped_column, Mapped

from app.database import utils
from app.database.types import ID, ID_UUID, GUID


# https://docs.sqlalchemy.org/en/20/core/defaults.html
# https://docs.sqlalchemy.org/en/20/orm/declarative_config.html#abstract
# https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#orm-declarative-mapped-column-type-map-pep593


class Mixin:
    pass


class IDMixin(Mixin):
    id: Mapped[ID] = mapped_column(
        Identity(), primary_key=True, sort_order=-100
    )


class UUIDMixin(Mixin):
    id: Mapped[ID_UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        sort_order=-100,
    )


class TimestampMixin(Mixin):
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), sort_order=100
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
        onupdate=utils.naive_utc,
        sort_order=101,
    )


class SoftRemovalMixin(Mixin):
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        sort_order=102
    )
