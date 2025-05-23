import pytest
from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from fastid.database.uow import SQLAlchemyUOW
from fastid.oauth.models import OAuthAccount
from fastid.oauth.schemas import OpenIDBearer
from tests import mocks


@pytest.mark.parametrize(
    ("provider", "openid"),
    [
        ("google", mocks.GOOGLE_OPENID_BEARER),
        ("yandex", mocks.YANDEX_OPENID_BEARER),
        ("telegram", mocks.TELEGRAM_OPENID_BEARER),
    ],
)
async def test_oauth_revoke(  # noqa: PLR0913
    client: AsyncClient,
    uow: SQLAlchemyUOW,
    user: UserDTO,
    user_token: TokenResponse,
    provider: str,
    openid: OpenIDBearer,
) -> None:
    oauth_account = OAuthAccount.from_open_id(openid, user.id)
    await uow.oauth_accounts.add(oauth_account)
    await uow.commit()

    response = await client.get(f"/oauth/revoke/{provider}")
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
