import base64
import os
import urllib.parse

from auth365.schemas import OAuth2Callback, TokenResponse
from httpx import AsyncClient
from starlette import status

from app.apps.schemas import AppDTO
from app.auth.backend import cookie_transport
from tests import mocks


async def authorize_password_grant(
    client: AsyncClient, username: str, password: str, scope: str = "offline_access"
) -> TokenResponse:
    response = await client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": username,
            "password": password,
            "scope": scope,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    return TokenResponse.model_validate_json(response.content)


async def authorize_refresh_token_grant(client: AsyncClient, oauth_app: AppDTO, token: TokenResponse) -> TokenResponse:
    response = await client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "refresh_token",
            "client_id": oauth_app.client_id,
            "client_secret": oauth_app.client_secret,
            "refresh_token": token.refresh_token,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    return TokenResponse.model_validate_json(response.content)


async def give_consent_for_authorization_code_flow(
    frontend_client: AsyncClient, oauth_app: AppDTO, token: TokenResponse, scope: str = "id_token offline_access"
) -> OAuth2Callback:
    redirect_uri = oauth_app.redirect_uris.split(";")[0]
    assert token.access_token is not None
    frontend_client.cookies.set(cookie_transport.name, token.access_token)
    response = await frontend_client.get(
        "/authorize",
        params={
            "response_type": "code",
            "client_id": oauth_app.client_id,
            "redirect_uri": redirect_uri,
            "state": mocks.STATE,
            "scope": scope,
        },
    )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

    loc = urllib.parse.urlparse(response.headers["Location"])
    query = urllib.parse.parse_qs(loc.query)
    return OAuth2Callback.model_validate({k: v[0] for k, v in query.items()})


async def authorize_authorization_code_grant(
    client: AsyncClient, oauth_app: AppDTO, callback: OAuth2Callback
) -> TokenResponse:
    response = await client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "client_id": oauth_app.client_id,
            "client_secret": oauth_app.client_secret,
            "code": callback.code,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    return TokenResponse.model_validate_json(response.content)


def generate_random_state(length: int = 64) -> str:
    bytes_length = int(length * 3 / 4)
    return base64.urlsafe_b64encode(os.urandom(bytes_length)).decode("utf-8")
