import datetime
import uuid
from enum import StrEnum, auto
from typing import Literal, Sequence, Self, assert_never

from pydantic import (
    Field,
    EmailStr,
    field_serializer,
    ConfigDict,
    model_validator,
)

from app.base.schemas import BaseModel


class TokenConfig(BaseModel):
    issuer: str | None = None
    audience: list[str] | None = None
    algorithm: str = "HS256"
    private_key: str
    public_key: str
    type: str
    expires_in: datetime.timedelta
    include: set[str] | None = None
    exclude: set[str] | None = None


class JWTClaims(BaseModel):
    jti: str | None = Field(default_factory=lambda: str(uuid.uuid4()))
    iss: str | None = None
    aud: list[str] | None = None
    typ: str | None = None
    sub: str | None = None
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    iat: datetime.datetime | None = None
    nbf: datetime.datetime | None = None
    exp: datetime.datetime | None = None

    @field_serializer("iat", "exp", "nbf", mode="plain")
    def datetime_to_timestamp(
        self, value: datetime.datetime | None
    ) -> int | None:
        if value is None:
            return value
        return int(value.timestamp())

    model_config = ConfigDict(extra="allow")


class BearerToken(BaseModel):
    token_id: str
    access_token: str
    refresh_token: str | None = None
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(
        description="Token expiration time in seconds",
    )


class VerifyToken(BaseModel):
    verify_token: str
    expires_in: int


class OAuth2Grant(StrEnum):
    authorization_code = auto()
    refresh_token = auto()
    password = auto()


class OAuth2TokenRequest(BaseModel):
    grant_type: OAuth2Grant = OAuth2Grant.password
    scope: str = ""
    client_id: str = "default"
    client_secret: str = "default"
    username: str | None = "user@example.com"
    password: str | None = "changethis"
    refresh_token: str | None = ""
    code: str | None = ""
    redirect_uri: str | None = ""
    code_verifier: str | None = ""

    @property
    def scopes(self) -> Sequence[str]:
        return self.scope.split(" ")

    @model_validator(mode="after")
    def validate_grant(self) -> Self:
        match self.grant_type:
            case OAuth2Grant.password:
                if not (self.username and self.password):
                    raise ValueError("username and password are required")
            case OAuth2Grant.refresh_token:
                if not self.refresh_token:
                    raise ValueError("refresh_token is required")
            case OAuth2Grant.authorization_code:
                if not (self.code and self.redirect_uri):
                    raise ValueError("code and redirect_uri are required")
            case _:
                assert_never(self.grant_type)
        return self
