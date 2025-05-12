from httpx import AsyncClient

from fastid.auth.schemas import UserDTO
from tests import mocks
from tests.utils.auth import authorize_password_grant


async def test_offline_access_scope(client: AsyncClient, user: UserDTO) -> None:
    assert user.email is not None
    token = await authorize_password_grant(client, user.email, mocks.USER_CREATE.password, scope="offline_access")
    assert token.refresh_token is not None
