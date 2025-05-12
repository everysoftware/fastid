from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.apps.schemas import AppDTO
from fastid.security.crypto import generate_otp
from tests.utils.auth import authorize_authorization_code_grant, get_ac_grant_callback


async def test_authorize_authorization_code_grant(
    client: AsyncClient, frontend_client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse
) -> None:
    callback = await get_ac_grant_callback(frontend_client, oauth_app, user_token)
    token = await authorize_authorization_code_grant(client, oauth_app, callback)
    assert token.access_token is not None
    assert token.refresh_token is not None
    assert token.id_token is not None


async def test_authorize_authorization_code_grant_fake_code(
    client: AsyncClient, frontend_client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse
) -> None:
    code = generate_otp()
    response = await client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "client_id": oauth_app.client_id,
            "client_secret": oauth_app.client_secret,
            "code": code,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
