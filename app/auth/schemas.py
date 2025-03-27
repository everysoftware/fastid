from auth365.schemas import (
    OAuth2ConsentRequest as BaseOAuth2ConsentRequest,
)
from auth365.schemas import (
    OAuth2TokenRequest as BaseOAuth2TokenRequest,
)
from pydantic import (
    Field,
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


class UserChangeEmail(BaseModel):
    new_email: str
    code: str


class UserChangePassword(BaseModel):
    password: str


class OAuth2TokenRequest(BaseOAuth2TokenRequest):
    pass


class OAuth2ConsentRequest(BaseOAuth2ConsentRequest):
    scope: str = "openid email name"
