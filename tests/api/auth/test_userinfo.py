from fastlink.jwt.schemas import JWTPayload
from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from fastid.database.utils import uuid_hex
from fastid.security.jwt import jwt_backend
from tests.mocks import faker


async def test_userinfo(client: AsyncClient, user: UserDTO, user_token: TokenResponse) -> None:
    response = await client.get("/userinfo", headers={"Authorization": f"Bearer {user_token.access_token}"})
    assert response.status_code == status.HTTP_200_OK
    actual_user = UserDTO.model_validate_json(response.content)
    assert actual_user == user


async def test_userinfo_user_not_exists(client: AsyncClient, user: UserDTO) -> None:
    at = jwt_backend.create("access", JWTPayload(sub=uuid_hex()))
    response = await client.get("/userinfo", headers={"Authorization": f"Bearer {at}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_userinfo_fake_token(client: AsyncClient, user: UserDTO) -> None:
    response = await client.get(
        "/userinfo",
        headers={"Authorization": f"Bearer {faker.pystr(min_chars=8, max_chars=256)}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_userinfo_refresh_token(client: AsyncClient, user: UserDTO, user_token: TokenResponse) -> None:
    response = await client.get("/userinfo", headers={"Authorization": f"Bearer {user_token.refresh_token}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_userinfo_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/userinfo")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
