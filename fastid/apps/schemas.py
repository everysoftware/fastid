import secrets

from fastid.apps.exceptions import InvalidClientCredentialsError, InvalidRedirectURIError
from fastid.core.schemas import BaseModel
from fastid.database.schemas import EntityDTO


class AppBase(BaseModel):
    name: str
    slug: str
    redirect_uris: str
    is_active: bool = True


class AppDTO(EntityDTO, AppBase):
    client_id: str
    client_secret: str


class ClientSnapshot(AppDTO):
    def verify_secret(self, client_secret: str) -> None:
        if not self.is_active or not secrets.compare_digest(client_secret, self.client_secret):
            raise InvalidClientCredentialsError

    def verify_redirect_uri(self, redirect_uri: str) -> None:
        if not self.is_active:
            raise InvalidClientCredentialsError
        if redirect_uri not in self.redirect_uris.split(";"):
            raise InvalidRedirectURIError


class AppCreate(AppBase):
    client_id: str | None = None
    client_secret: str | None = None


class AppUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    redirect_uris: str | None = None
    is_active: bool | None = None
    client_id: str | None = None
    client_secret: str | None = None
