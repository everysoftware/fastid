from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from tests import mocks
from tests.utils.auth import authorize_password_grant


async def test_admin_scope(client: AsyncClient, user_su: UserDTO) -> None:
    assert user_su.email is not None
    token = await authorize_password_grant(client, user_su.email, mocks.USER_SU_CREATE.password, scope="admin")
    assert token.access_token is not None


async def test_admin_scope_not_su(client: AsyncClient, user: UserDTO) -> None:
    response = await client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": user.email,
            "password": mocks.USER_CREATE.password,
            "scope": "admin",
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
