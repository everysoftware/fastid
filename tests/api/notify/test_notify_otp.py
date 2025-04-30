from auth365.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from fastid.cache.storage import CacheStorage
from fastid.security.crypto import generate_otp


async def test_notify_otp(client: AsyncClient, cache: CacheStorage, user: UserDTO, user_token: TokenResponse) -> None:
    response = await client.post("/notify/otp", headers={"Authorization": f"Bearer {user_token.access_token}"})
    assert response.status_code == status.HTTP_200_OK

    await cache.get(f"otp:users:{user.id}")


async def test_notify_verify_token(
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
