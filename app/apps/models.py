import secrets

from sqlalchemy.orm import Mapped, mapped_column

from app.apps.exceptions import InvalidClientCredentialsError, InvalidRedirectURIError
from app.base.datatypes import uuid_hex
from app.base.models import Entity


class App(Entity):
    __tablename__ = "apps"

    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True)
    client_id: Mapped[str] = mapped_column(default=uuid_hex)
    client_secret: Mapped[str] = mapped_column(default=uuid_hex)
    redirect_uris: Mapped[str] = mapped_column(default="")
    is_active: Mapped[bool] = mapped_column(default=True)

    def verify_redirect_uri(self, redirect_uri: str) -> None:
        if redirect_uri not in self.redirect_uris.split(";"):
            raise InvalidRedirectURIError

    def verify_secret(self, client_secret: str) -> None:
        if not secrets.compare_digest(client_secret, self.client_secret):
            raise InvalidClientCredentialsError
