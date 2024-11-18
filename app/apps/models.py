import secrets

from sqlalchemy.orm import Mapped, mapped_column

from app.apps.exceptions import InvalidRedirectURI, InvalidClientCredentials
from app.auth.schemas import OAuth2ConsentRequest
from app.authlib.oauth import OAuth2AuthorizationCodeRequest
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

    def check_consent_request(self, consent: OAuth2ConsentRequest) -> None:
        if consent.redirect_uri not in self.redirect_uris.split(";"):
            raise InvalidRedirectURI()

    def check_token_request(
        self, request: OAuth2AuthorizationCodeRequest
    ) -> None:
        if not secrets.compare_digest(
            request.client_secret, self.client_secret
        ):
            raise InvalidClientCredentials()
