from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from fastid.cache.storage import CacheStorage
from tests.mocks import faker


async def test_notify_otp_email(
    client: AsyncClient, cache: CacheStorage, user: UserDTO, user_token: TokenResponse
) -> None:
    response = await client.post("/notify/otp", headers={"Authorization": f"Bearer {user_token.access_token}"})
    assert response.status_code == status.HTTP_200_OK

    await cache.get(f"otp:users:{user.id}")


async def test_notify_otp_new_email(
    client: AsyncClient, cache: CacheStorage, user: UserDTO, user_token: TokenResponse
) -> None:
    response = await client.post(
        f"/notify/otp?new_email={faker.email()}", headers={"Authorization": f"Bearer {user_token.access_token}"}
    )
    assert response.status_code == status.HTTP_200_OK

    await cache.get(f"otp:users:{user.id}")


async def test_notify_otp_telegram(
    client: AsyncClient, cache: CacheStorage, user_tg: UserDTO, user_tg_token: TokenResponse
) -> None:
    response = await client.post("/notify/otp", headers={"Authorization": f"Bearer {user_tg_token.access_token}"})
    assert response.status_code == status.HTTP_200_OK

    await cache.get(f"otp:users:{user_tg.id}")
