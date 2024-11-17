import datetime
from typing import Literal

from pydantic import Field, EmailStr, field_serializer, ConfigDict

from app.base.schemas import BaseModel
from app.base.types import uuid


class TypeParams(BaseModel):
    algorithm: str = "HS256"
    private_key: str
    public_key: str
    expires_in: datetime.timedelta
    issuer: str = "unnamed_app"


class JWTClaims(BaseModel):
    iss: str | None = None
    sub: str | None = None
    aud: str | None = None
    typ: str | None = None
    iat: datetime.datetime | None = None
    exp: datetime.datetime | None = None

    @field_serializer("iat", "exp", mode="plain")
    def datetime_to_timestamp(
        self, value: datetime.datetime | None
    ) -> int | None:
        if value is None:
            return value
        return int(value.timestamp())

    model_config = ConfigDict(extra="allow")


class AccessTokenClaims(JWTClaims):
    scope: str | None = None


class RefreshTokenClaims(JWTClaims):
    scope: str | None = None


class IDTokenClaims(JWTClaims):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None


class TokenResponse(BaseModel):
    token_id: str = Field(default_factory=lambda: uuid().hex)
    access_token: str | None = None
    refresh_token: str | None = None
    id_token: str | None = None
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(
        description="Token expiration time in seconds",
    )
