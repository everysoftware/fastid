from auth365.schemas import TokenResponse
from httpx import AsyncClient

from app.apps.schemas import AppDTO
from app.auth.schemas import UserDTO
from tests import mocks
from tests.utils.auth import (
    authorize_authorization_code_grant,
    authorize_password_grant,
    authorize_refresh_token_grant,
    give_oauth_consent,
)


async def test_authorize_password_grant(client: AsyncClient, user: UserDTO) -> None:
    assert user.email is not None
    token = await authorize_password_grant(client, user.email, mocks.USER_CREATE.password)
    assert token.access_token is not None
    assert token.refresh_token is not None


async def test_authorize_refresh_token_grant(client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse) -> None:
    token = await authorize_refresh_token_grant(client, oauth_app, user_token)
    assert token.access_token is not None
    assert token.refresh_token is not None


async def test_give_oauth_consent(frontend_client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse) -> None:
    callback = await give_oauth_consent(frontend_client, oauth_app, user_token)
    assert callback.state is not None
    assert callback.state == mocks.STATE
    assert callback.code is not None
    assert callback.code
    assert callback.redirect_uri is not None
    assert callback.redirect_uri == callback.redirect_uri


async def test_authorize_authorization_code_grant(
    client: AsyncClient, frontend_client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse
) -> None:
    callback = await give_oauth_consent(frontend_client, oauth_app, user_token)
    token = await authorize_authorization_code_grant(client, oauth_app, callback)
    assert token.access_token is not None
    assert token.refresh_token is not None
    assert token.id_token is not None
