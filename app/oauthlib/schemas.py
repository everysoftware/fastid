from typing import Literal

import pydantic
from pydantic import AnyHttpUrl, ConfigDict

from app.base.schemas import BaseModel

type AnyUrl = pydantic.AnyHttpUrl | str


class DiscoveryDocument(BaseModel):
    authorization_endpoint: str | None = None
    token_endpoint: str | None = None
    userinfo_endpoint: str | None = None

    model_config = ConfigDict(extra="allow")


class OAuthCallback(BaseModel):
    code: str
    state: str | None = None
    scope: str | None = None
    code_verifier: str | None = None
    redirect_uri: AnyHttpUrl | None = None

    @property
    def scopes(self) -> list[str] | None:
        if self.scope is not None:
            return self.scope.split()
        return None


class OAuthBearerToken(BaseModel):
    access_token: str
    token_type: Literal["Bearer", "bearer"] = "Bearer"
    id_token: str | None = None
    refresh_token: str | None = None
    expires_in: int | None = None
    scope: str | None = None

    @property
    def scopes(self) -> list[str] | None:
        if self.scope is not None:
            return self.scope.split()
        return None


class OpenID(BaseModel):
    id: str
    provider: str
    email: pydantic.EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    picture: str | None = None


class TelegramCallback(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


class OpenIDBearer(OpenID, OAuthBearerToken):
    pass
