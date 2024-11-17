"""
OAuth 2.0

OAuth 2.0 is a protocol that allows a user to grant a third-party website or application access to the user's
protected resources, without necessarily revealing their long-term credentials or even their identity.

Agents:

* Resource owner (user), e.g. Petya
* Client (application), e.g. SuperApp
* Authorization server, e.g. Google
* Resource server (provider), e.g. Google Photos
"""

from enum import StrEnum, auto
from typing import Iterable, Sequence

from pydantic import (
    ConfigDict,
)

from app.base.schemas import BaseModel


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
    The client directs the resource owner to an resource server. The resource owner authenticates and authorizes
    the client. The authorization server redirects the resource owner back to the client with an authorization code.
    The client requests an access token from the authorization server's token endpoint by including the authorization
    code received in the previous step.
    """
    pkce = auto()
    """
    The client directs the resource owner to an resource server. The resource owner authenticates and authorizes
    the client. The authorization server redirects the resource owner back to the client with an authorization code.
    The client requests an access token from the authorization server's token endpoint by including the authorization
    code received in the previous step and the code verifier.
    """
    refresh_token = auto()
    """
    The client requests an access token from the authorization server's token endpoint by including the refresh token
    """


class OAuth2ResponseType(StrEnum):
    """
    Response Types are used to specify the desired authorization processing flow.
    """

    token = auto()
    """
    Used for the implicit flow to obtain an access token.
    """
    id_token = auto()
    """
    Used for the implicit flow to obtain an ID Token.
    """
    code = auto()
    """
    Used for the authorization code flow to obtain an authorization code.
    """


class OAuth2ConsentRequest(BaseModel):
    """
    OAuth 2.0 Consent Request
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
    def response_types(self) -> Sequence[OAuth2ResponseType] | None:
        if self.response_type is not None:
            return [
                OAuth2ResponseType(s) for s in self.response_type.split(" ")
            ]
        return None


class OAuth2BaseTokenRequest(BaseModel):
    grant_type: OAuth2Grant
    """
    The grant type is used to specify the method through which a client can obtain an access token.
    """
    client_id: str = "default"
    """
    The client ID is a public identifier for the client.

    Client credentials may be omitted if the resource server trusts the client. E.g. if you are connecting
    backend and frontend of the same application.
    """
    client_secret: str = "default"
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
