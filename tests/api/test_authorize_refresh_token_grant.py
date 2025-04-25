from auth365.schemas import TokenResponse
from httpx import AsyncClient

from app.apps.schemas import AppDTO
from tests.utils.auth import authorize_refresh_token_grant


async def test_authorize_refresh_token_grant(client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse) -> None:
    token = await authorize_refresh_token_grant(client, oauth_app, user_token)
    assert token.access_token is not None
    assert token.refresh_token is not None
