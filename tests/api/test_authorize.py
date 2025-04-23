from auth365.schemas import TokenResponse
from httpx import AsyncClient

from app.apps.schemas import AppDTO
from tests import mocks
from tests.utils.auth import (
    authorize_authorization_code_grant,
    authorize_refresh_token_grant,
    give_consent_for_authorization_code_flow,
)


def test_authorize_password_grant(user_token: TokenResponse) -> None:
    assert user_token.access_token is not None
    assert user_token.refresh_token is not None


async def test_authorize_refresh_token_grant(client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse) -> None:
    new_token = await authorize_refresh_token_grant(client, oauth_app, user_token)
    assert new_token.access_token is not None
    assert new_token.refresh_token is not None


async def test_authorize_authorization_code_grant(
    client: AsyncClient, frontend_client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse
) -> None:
    callback = await give_consent_for_authorization_code_flow(frontend_client, oauth_app, user_token)
    assert callback.state is not None
    assert callback.state == mocks.STATE
    assert callback.code is not None
    assert callback.code
    assert callback.redirect_uri is not None
    assert callback.redirect_uri == callback.redirect_uri

    token = await authorize_authorization_code_grant(client, oauth_app, callback)
    assert token.access_token is not None
    assert token.refresh_token is not None
    assert token.id_token is not None
