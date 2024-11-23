from typing import Literal

from pydantic import (
    Field,
)

from app.authlib.oauth import (
    OAuth2TokenRequest as AuthlibOAuth2TokenRequest,
    OAuth2ConsentRequest as AuthlibOAuth2ConsentRequest,
)
from app.base.schemas import BaseModel, EntityDTO

ContactType = Literal["email", "telegram"]


class Contact(BaseModel):
    type: ContactType
    value: str


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


class UserChangeEmail(BaseModel):
    new_email: str
    code: str


class UserChangePassword(BaseModel):
    password: str


class OAuth2TokenRequest(AuthlibOAuth2TokenRequest):
    pass


class OAuth2ConsentRequest(AuthlibOAuth2ConsentRequest):
    scope: str = "openid email name"
