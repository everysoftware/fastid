from enum import StrEnum, auto

from pydantic import (
    Field,
)

from app.authlib.oauth import (
    OAuth2TokenRequest as AuthlibOAuth2TokenRequest,
    OAuth2ConsentRequest as AuthlibOAuth2ConsentRequest,
)
from app.base.schemas import BaseModel, EntityDTO


class UserDTO(EntityDTO):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    hashed_password: str | None = Field(None, exclude=True)
    telegram_id: int | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None


class UserCreate(BaseModel):
    first_name: str = Field(examples=["John"])
    last_name: str | None = Field(None, examples=["Doe"])
    email: str
    password: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None


class TokenType(StrEnum):
    access = auto()
    refresh = auto()
    verify = auto()


class Role(StrEnum):
    user = auto()
    superuser = auto()


class Scope(StrEnum):
    """
    Scopes are strings that are used to specify what access rights an access token has.
    """

    profile = auto()
    """
    Access to the user's profile.
    """
    openid = auto()
    """
    Access to the user's ID Token. This is required for OpenID Connect.
    """
    admin = auto()
    """
    Access to the admin panel.
    """


class OAuth2TokenRequest(AuthlibOAuth2TokenRequest):
    pass


class OAuth2ConsentRequest(AuthlibOAuth2ConsentRequest):
    pass
