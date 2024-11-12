import uuid

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseEntityOrm


class AppOrm(BaseEntityOrm):
    __tablename__ = "apps"

    name: Mapped[str]
    client_id: Mapped[str] = mapped_column(default=lambda x: uuid.uuid4().hex)
    client_secret: Mapped[str] = mapped_column(
        default=lambda x: uuid.uuid4().hex
    )
    redirect_uris: Mapped[str] = mapped_column(default="")
    is_active: Mapped[bool] = mapped_column(default=True)
