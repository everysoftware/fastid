import datetime

from pydantic import ConfigDict, field_serializer, EmailStr

from app.base.schemas import BaseModel


class DiscoveryDocument(BaseModel):
    """
    OpenID Connect Discovery Document.
    """

    authorization_endpoint: str = ""
    token_endpoint: str = ""
    userinfo_endpoint: str = ""

    model_config = ConfigDict(extra="allow")


class TypeParams(BaseModel):
    algorithm: str = "HS256"
    private_key: str
    public_key: str
    expires_in: datetime.timedelta | None = None
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
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    email: EmailStr | None = None
    email_verified: bool | None = None
