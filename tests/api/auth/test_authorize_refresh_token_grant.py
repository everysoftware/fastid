from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.apps.schemas import AppDTO
from fastid.database.utils import uuid
from tests.mocks import faker


async def test_authorize_refresh_token_grant(client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse) -> None:
    response = await client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "refresh_token",
            "client_id": oauth_app.client_id,
            "client_secret": oauth_app.client_secret,
            "refresh_token": user_token.refresh_token,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    token = TokenResponse.model_validate_json(response.content)
    assert token.access_token is not None
    assert token.refresh_token is not None


async def test_authorize_refresh_token_grant_fake_token(
    client: AsyncClient,
    oauth_app: AppDTO,
    user_token: TokenResponse,
) -> None:
    response = await client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "refresh_token",
            "client_id": oauth_app.client_id,
            "client_secret": oauth_app.client_secret,
            "refresh_token": faker.pystr(min_chars=8, max_chars=256),
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_authorize_refresh_token_grant_invalid_client_id(
    client: AsyncClient,
    oauth_app: AppDTO,
    user_token: TokenResponse,
) -> None:
    response = await client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "refresh_token",
            "client_id": uuid(),
            "client_secret": oauth_app.client_secret,
            "refresh_token": user_token.refresh_token,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_authorize_refresh_token_grant_invalid_client_secret(
    client: AsyncClient,
    oauth_app: AppDTO,
    user_token: TokenResponse,
) -> None:
    response = await client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "refresh_token",
            "client_id": oauth_app.client_id,
            "client_secret": uuid(),
            "refresh_token": user_token.refresh_token,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
