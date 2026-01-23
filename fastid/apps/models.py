import secrets

from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastid.apps.exceptions import InvalidClientCredentialsError, InvalidRedirectURIError
from fastid.database.base import VersionedEntity
from fastid.database.utils import uuid_hex
from fastid.webhooks.models import Webhook


class App(VersionedEntity):
    __tablename__ = "apps"

    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True)
    client_id: Mapped[str] = mapped_column(default=uuid_hex)
    client_secret: Mapped[str] = mapped_column(default=uuid_hex)
    redirect_uris: Mapped[str] = mapped_column(default="")
    is_active: Mapped[bool] = mapped_column(default=True)

    webhooks: Mapped[list[Webhook]] = relationship(back_populates="app", cascade="delete")

    def verify_redirect_uri(self, redirect_uri: str) -> None:
        if redirect_uri not in self.redirect_uris.split(";"):
            raise InvalidRedirectURIError

    def verify_secret(self, client_secret: str) -> None:
        if not secrets.compare_digest(client_secret, self.client_secret):
            raise InvalidClientCredentialsError
