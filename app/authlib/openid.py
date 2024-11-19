"""
OpenID Connect (OIDC) is an authentication protocol that is built on top of OAuth 2.0. OpenID Connect provides a
standardized way for clients to authenticate users and obtain their information. OpenID Connect defines an ID token
that is used to authenticate a user

Agents:

* Identity Provider (IDP): The Identity Provider is the service that authenticates the user and provides the user's information to the client.

* Client: The Client is the application that wants to authenticate the user and obtain the user's information.

* User: The User is the person who is using the client application.
"""

import datetime
from typing import Sequence, Literal

from pydantic import ConfigDict, field_serializer, EmailStr

from app.base.schemas import BaseModel


class DiscoveryDocument(BaseModel):
    """
    Discovery Document is a JSON document that contains key-value pairs of metadata about the OpenID Connect provider.
    """

    issuer: str | None = None
    authorization_endpoint: str | None = None
    token_endpoint: str | None = None
    userinfo_endpoint: str | None = None
    jwks_uri: str | None = None
    scopes_supported: Sequence[str] | None = None
    response_types_supported: Sequence[str] | None = None
    grant_types_supported: Sequence[str] | None = None
    subject_types_supported: Sequence[str] | None = None
    id_token_signing_alg_values_supported: Sequence[str] | None = None
    claims_supported: Sequence[str] | None = None

    model_config = ConfigDict(extra="allow")


class JWK(BaseModel):
    """
    JSON Web Key (JWK) is a JSON object that represents a cryptographic key.
    """

    kty: str
    use: str
    alg: str
    kid: str
    n: str
    e: str

    model_config = ConfigDict(extra="allow")


class JWKS(BaseModel):
    keys: Sequence[JWK]


class JWTClaims(BaseModel):
    """
    JSON Web Token (JWT) Claims are the JSON objects that contain the information about the user and the token itself.
    """

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
    """
    Access Token is a JSON Web Token (JWT) that contains the information about the user and the permissions that the
    user has. Access Token is used to access the protected resources.
    """

    scope: str | None = None


class RefreshTokenClaims(JWTClaims):
    """
    Refresh Token is a JSON Web Token (JWT) that used to obtain a new Access Token when the current Access Token
    expires. Refresh Token is used to refresh the Access Token without the need to re-authenticate the user.
    """

    scope: str | None = None


class IDTokenClaims(JWTClaims):
    """
    ID Token is a JSON Web Token (JWT) that contains the information about the user and the authentication process.
    ID Token is used to authenticate the user and to obtain the user's information.
    """

    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    email: EmailStr | None = None
    email_verified: bool | None = None


class JWTParams(BaseModel):
    issuer: str
    algorithm: Literal["HS256", "RS256"] = "RS256"
    private_key: str
    public_key: str
    expires_in: datetime.timedelta | None = None
