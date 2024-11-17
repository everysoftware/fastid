from sqlalchemy.orm import Mapped, mapped_column

from app.base.models import Entity
from app.base.types import uuid_hex


class App(Entity):
    __tablename__ = "apps"

    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True)
    client_id: Mapped[str] = mapped_column(default=uuid_hex)
    client_secret: Mapped[str] = mapped_column(default=uuid_hex)
    redirect_uris: Mapped[str] = mapped_column(default="")
    is_active: Mapped[bool] = mapped_column(default=True)
