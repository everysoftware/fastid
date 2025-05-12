from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from tests import mocks
from tests.mocks import faker
from tests.utils.auth import (
    authorize_password_grant,
)


async def test_authorize_password_grant(client: AsyncClient, user: UserDTO) -> None:
    assert user.email is not None
    token = await authorize_password_grant(client, user.email, mocks.USER_CREATE.password)
    assert token.access_token is not None
    assert token.refresh_token is not None


async def test_authorize_password_grant_not_exists(client: AsyncClient) -> None:
    response = await client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": faker.email(),
            "password": mocks.USER_CREATE.password,
            "scope": "offline_access",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_authorize_password_grant_wrong_password(client: AsyncClient, user: UserDTO) -> None:
    response = await client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": user.email,
            "password": faker.password(),
            "scope": "offline_access",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
