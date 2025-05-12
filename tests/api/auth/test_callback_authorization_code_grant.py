from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.apps.schemas import AppDTO
from fastid.auth.dependencies import cookie_transport
from tests import mocks
from tests.mocks import faker
from tests.utils.auth import get_ac_grant_callback


async def test_ac_grant_callback(frontend_client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse) -> None:
    callback = await get_ac_grant_callback(frontend_client, oauth_app, user_token)
    assert callback.state is not None
    assert callback.state == mocks.OAUTH_STATE
    assert callback.code is not None
    assert callback.code
    assert callback.redirect_uri is not None
    assert callback.redirect_uri == callback.redirect_uri


async def test_ac_grant_callback_invalid_redirect_uri(
    frontend_client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse
) -> None:
    assert user_token.access_token is not None
    frontend_client.cookies.set(cookie_transport.name, user_token.access_token)
    response = await frontend_client.get(
        "/authorize",
        params={
            "response_type": "code",
            "client_id": oauth_app.client_id,
            "redirect_uri": faker.uri(schemes=["https"]),
            "state": mocks.OAUTH_STATE,
            "scope": "openid offline_access",
        },
    )
    frontend_client.cookies.delete(cookie_transport.name)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_ac_grant_callback_invalid_response_type(
    frontend_client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse
) -> None:
    redirect_uri = oauth_app.redirect_uris.split(";")[0]
    assert user_token.access_token is not None
    frontend_client.cookies.set(cookie_transport.name, user_token.access_token)
    response = await frontend_client.get(
        "/authorize",
        params={
            "response_type": "not_code",
            "client_id": oauth_app.client_id,
            "redirect_uri": redirect_uri,
            "state": mocks.OAUTH_STATE,
            "scope": "openid offline_access",
        },
    )
    frontend_client.cookies.delete(cookie_transport.name)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
