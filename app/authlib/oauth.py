"""
OAuth 2.0

OAuth 2.0 is a protocol that allows a user to grant a third-party website or application access to the user's
protected resources, without necessarily revealing their long-term credentials or even their identity.

Agents:

* Resource owner (user), e.g. Petya
* Client (application), e.g. SuperApp
* Authorization server, e.g. Google
* Resource server (provider), e.g. Google Photos

Terms:

Identification - the process of identifying a user. It can be done by a name, email, id or phone number.

Authentication - the process of verifying the identity of a user. It can be done by a password, fingerprint, or
face recognition. OpenID Connect defines an ID token that is used to authenticate a user.

Authorization - the process of granting permissions to a user. It can be done by a scope, role, or permission.
OAuth 2.0 defines an access token that is used to authorize a user.
"""

from enum import StrEnum, auto
from typing import Iterable
from urllib.parse import urlencode

from pydantic import (
    ConfigDict,
    Field,
)

from app.base.schemas import BaseModel
from app.base.types import uuid


class OAuth2Grant(StrEnum):
    """
    Grants are methods through which a client can obtain an access token.
    """

    client_credentials = auto()
    """
    The client requests an access token from the authorization server's token endpoint by including its client
    credentials (client_id and client_secret). This is used when the client is acting on its own behalf.
    """
    password = auto()
    """
    The resource owner provides the client with its username and password.
    The client requests an access token from the authorization server's token endpoint by including the credentials
    received from the resource owner.

    This grant type should only be used when there is a high degree of trust between the resource owner and the client.
    """
    implicit = auto()
    """
    The client directs the resource owner to the authorization server. The resource owner authenticates and
    authorizes the client. The authorization server redirects the resource owner back to the client with an access
    token.

    This grant type is used for clients that are implemented in a browser using a scripting language such as JavaScript.
    """
    authorization_code = auto()
    """
    The client directs the resource owner to an authorization server. The resource owner authenticates and authorizes
    the client. The authorization server redirects the resource owner back to the client with an authorization code.
    The client requests an access token from the authorization server's token endpoint by including the authorization
    code received in the previous step.
    """
    pkce = auto()
    """
    The client directs the resource owner to an authorization server. The resource owner authenticates and authorizes
    the client. The authorization server redirects the resource owner back to the client with an authorization code.
    The client requests an access token from the authorization server's token endpoint by including the authorization
    code received in the previous step and the code verifier.
    """
    refresh_token = auto()
    """
    The client requests an access token from the authorization server's token endpoint by including the refresh token
    """


class OAuth2ConsentRequest(BaseModel):
    """
    Consent Request is sent by the client to the authorization server.
    Authorization server asks the resource owner to grant permissions to the client.
    """

    response_type: str | None = None
    """
    The response type is used to specify the desired authorization processing flow.
    """
    client_id: str | None = None
    """
    The client ID is a public identifier for the client.
    """
    redirect_uri: str | None = None
    """
    The redirect URI is used to redirect the user-agent back to the client.
    """
    scope: str | None = None
    """
    The scope is used to specify what access rights an access token has.
    """
    state: str | None = None
    """
    The state is used to prevent CSRF attacks.
    """
    code_challenge: str | None = None
    """
    The code challenge is used to verify the authorization code.
    """
    code_challenge_method: str | None = None
    """
    The code challenge method is used to verify the authorization code.
    """

    @property
    def scopes(self) -> Iterable[str]:
        if self.scope is None:
            return []
        return self.scope.split(" ")


class OAuth2Callback(BaseModel):
    """
    Callback is sent by the authorization server to the client after the resource owner grants permissions.
    """

    code: str | None = None
    """
    The authorization code is used to obtain an access token.
    """
    state: str | None = None
    """
    The state is used to prevent CSRF attacks. State should be the same as in the consent request.
    """
    scope: str | None = None
    """
    The scope is used to specify what access rights an access token has. Scope should be the same as in the consent
    request.
    """
    code_verifier: str | None = None
    """
    The code verifier is used to verify the authorization code.
    """
    redirect_uri: str | None = None
    """
    The redirect URI is used to redirect the user-agent back to the client. Not all providers put it in the callback.
    """

    def get_url(self) -> str:
        return f"{self.redirect_uri}?{urlencode(self.model_dump(mode="json", exclude_none=True))}"


class OAuth2BaseTokenRequest(BaseModel):
    grant_type: OAuth2Grant
    """
    The grant type is used to specify the method through which a client can obtain an access token.
    """
    client_id: str = ""
    """
    The client ID is a public identifier for the client.

    Client credentials may be omitted if the resource server trusts the client. E.g. if you are connecting
    backend and frontend of the same application.
    """
    client_secret: str = ""
    """
    The client secret is a secret known only to the client and the resource server.

    May be omitted if the request comes from public clients (e.g. web browser).
    Client credentials may be omitted if the resource server trusts the client. E.g. if you are connecting
    backend and frontend of the same application.
    """

    model_config = ConfigDict(from_attributes=True)


class OAuth2PasswordRequest(OAuth2BaseTokenRequest):
    grant_type: OAuth2Grant = OAuth2Grant.password
    username: str = "user@example.com"
    """
    The resource owner's username. Used in Password Grant Flow.
    """
    password: str = "password"
    """
    The resource owner's password. Used in Password Grant Flow.
    """
    scope: str = ""
    """
    The scope is used to specify what access rights an access token has.

    Usually, it is passed as query params in the authorization URL, but if the flow does not assume redirection
    (like Password Grant Flow), it should be passed in the token request.
    """

    @property
    def scopes(self) -> Iterable[str]:
        return self.scope.split(" ")


class OAuth2AuthorizationCodeRequest(OAuth2BaseTokenRequest):
    grant_type: OAuth2Grant = OAuth2Grant.authorization_code
    code: str
    """
    The authorization code is used to obtain an access token. Used in Authorization Code Grant.
    """
    code_verifier: str = ""
    """
    The code verifier is used to verify the authorization code. Used in PKCE Grant.
    """
    redirect_uri: str = ""
    """
    The redirect URI is passed as second factor to authorize the client.

    Usually we passed the redirect URI in authorization URL, but some providers like Google oblige to pass it in token
    request too.
    """


class OAuth2RefreshTokenRequest(OAuth2BaseTokenRequest):
    grant_type: OAuth2Grant = OAuth2Grant.refresh_token
    refresh_token: str
    """
    The refresh token is used to obtain a new access token. Used in Refresh Token Grant.
    """


class OAuth2TokenRequest(BaseModel):
    """
    Token Request is sent by the client to the authorization server to obtain an access token.
    """

    grant_type: OAuth2Grant = OAuth2Grant.password
    client_id: str = ""
    client_secret: str = ""
    username: str = ""
    password: str = ""
    code: str = ""
    code_verifier: str = ""
    redirect_uri: str = ""
    refresh_token: str = ""
    scope: str = ""

    @property
    def scopes(self) -> Iterable[str]:
        return self.scope.split(" ")

    def as_password_grant(self) -> OAuth2PasswordRequest:
        return OAuth2PasswordRequest.model_validate(self)

    def as_authorization_code_grant(
        self,
    ) -> OAuth2AuthorizationCodeRequest:
        return OAuth2AuthorizationCodeRequest.model_validate(self)

    def as_refresh_token_grant(self) -> OAuth2RefreshTokenRequest:
        return OAuth2RefreshTokenRequest.model_validate(self)


class TokenResponse(BaseModel):
    """
    Token Response is sent by the authorization server to the client and contains the access token.
    """

    token_id: str | None = Field(default_factory=lambda: uuid().hex)
    access_token: str | None = None
    refresh_token: str | None = None
    id_token: str | None = None
    token_type: str | None = "bearer"
    scope: str | None = None
    expires_in: int | None = Field(
        None,
        description="Token expiration time in seconds",
    )
