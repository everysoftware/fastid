from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from fastid.cache.storage import CacheStorage
from fastid.security.crypto import generate_otp


async def test_get_verify_token(
    client: AsyncClient, cache: CacheStorage, user: UserDTO, user_token: TokenResponse
) -> None:
    code = generate_otp()
    await cache.set(f"otp:users:{user.id}", code)

    response = await client.post(
        "/notify/verify-token",
        json={
            "code": code,
        },
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["verify_token"] is not None


async def test_get_verify_token_not_exists(
    client: AsyncClient, cache: CacheStorage, user: UserDTO, user_token: TokenResponse
) -> None:
    code = generate_otp()
    response = await client.post(
        "/notify/verify-token",
        json={
            "code": code,
        },
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_get_verify_token_wrong_code(
    client: AsyncClient, cache: CacheStorage, user: UserDTO, user_token: TokenResponse
) -> None:
    code = generate_otp()
    fake_code = generate_otp()
    await cache.set(f"otp:users:{user.id}", code)
    response = await client.post(
        "/notify/verify-token",
        json={
            "code": fake_code,
        },
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
