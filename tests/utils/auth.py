import base64
import os
import urllib.parse
from typing import Any

from fastlink.schemas import OAuth2Callback, TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.apps.schemas import AppDTO
from fastid.auth.dependencies import cookie_transport
from fastid.auth.models import User
from fastid.auth.schemas import UserDTO
from fastid.database.uow import SQLAlchemyUOW
from tests import mocks


async def register_user(uow: SQLAlchemyUOW, data: dict[str, Any]) -> UserDTO:
    record = User(**data)
    await uow.users.add(record)
    await uow.commit()
    user = UserDTO.model_validate(record)
    user.hashed_password = None
    return user


async def authorize_password_grant(
    client: AsyncClient,
    username: str,
    password: str,
    scope: str = "offline_access",
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


async def get_ac_grant_callback(
    frontend_client: AsyncClient,
    oauth_app: AppDTO,
    token: TokenResponse,
    scope: str = "openid offline_access",
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
            "state": mocks.OAUTH_STATE,
            "scope": scope,
        },
    )
    frontend_client.cookies.delete(cookie_transport.name)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

    loc = urllib.parse.urlparse(response.headers["Location"])
    query = urllib.parse.parse_qs(loc.query)
    return OAuth2Callback.model_validate({k: v[0] for k, v in query.items()})


async def authorize_authorization_code_grant(
    client: AsyncClient,
    oauth_app: AppDTO,
    callback: OAuth2Callback,
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
