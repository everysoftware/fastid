import pytest
from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from fastid.database.schemas import PageDTO
from fastid.database.uow import SQLAlchemyUOW
from fastid.oauth.models import OAuthAccount
from fastid.oauth.schemas import OAuthAccountDTO, OpenIDBearer
from tests import mocks


@pytest.mark.parametrize(
    ("provider", "openid"),
    [
        ("google", mocks.GOOGLE_OPENID_BEARER),
        ("yandex", mocks.YANDEX_OPENID_BEARER),
        ("telegram", mocks.TELEGRAM_OPENID_BEARER),
    ],
)
async def test_oauth_get_many(  # noqa: PLR0913
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

    response = await client.get("/oauth/accounts")
    page = PageDTO[OAuthAccountDTO].model_validate_json(response.content)
    assert page.total == 1
    assert page.items[0] == OAuthAccountDTO.model_validate(oauth_account)
    assert response.status_code == status.HTTP_200_OK
