import datetime
from collections.abc import Sequence
from typing import Literal, Self

from pydantic import ConfigDict, EmailStr, field_serializer, model_validator

from fastid.core.schemas import BaseModel


class JWTPayload(BaseModel):
    """
    JSON Web Token (JWT) Claims are the JSON objects that contain the information about the user and the token itself.
    """

    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    email: EmailStr | None = None
    email_verified: bool | None = None
    scope: str | None = None

    iss: str | None = None
    sub: str | None = None
    aud: str | None = None
    typ: str | None = None
    iat: datetime.datetime | None = None
    exp: datetime.datetime | None = None

    @property
    def scopes(self) -> Sequence[str]:
        if self.scope is None:
            return []
        return self.scope.split(" ")

    @field_serializer("iat", "exp", mode="plain")
    def datetime_to_timestamp(self, value: datetime.datetime | None) -> int | None:
        if value is None:
            return value
        return int(value.timestamp())

    model_config = ConfigDict(extra="allow")


class JWTConfig(BaseModel):
    type: str
    algorithm: Literal["HS256", "RS256"] = "HS256"
    expires_in: datetime.timedelta = datetime.timedelta(hours=1)
    key: str | None = None
    issuer: str | None = None
    private_key: str | None = None
    public_key: str | None = None

    @model_validator(mode="after")
    def validate_key(self) -> Self:
        if self.algorithm == "HS256":
            if not self.key:
                msg = "Key is required for HS256 algorithm"
                raise ValueError(msg)
            self.private_key = self.key
            self.public_key = self.key
        else:
            if not self.private_key:
                msg = "Private key is required for RS256 algorithm"
                raise ValueError(msg)
            if not self.public_key:
                msg = "Public key is required for RS256 algorithm"
                raise ValueError(msg)
        return self
