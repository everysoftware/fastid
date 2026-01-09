from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from fastid.cache.storage import CacheStorage
from fastid.notify.schemas import UserAction
from tests.mocks import faker


async def test_send_otp(client: AsyncClient, cache: CacheStorage, user: UserDTO, user_token: TokenResponse) -> None:
    response = await client.post(
        f"/otp/send?action={UserAction.change_password}",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    await cache.get(f"otp:users:{user.id}")


async def test_send_otp_change_email(
    client: AsyncClient, cache: CacheStorage, user: UserDTO, user_token: TokenResponse
) -> None:
    response = await client.post(
        f"/otp/send?action={UserAction.change_email}&email={faker.email()}",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    await cache.get(f"otp:users:{user.id}")


async def test_send_otp_recover_password(client: AsyncClient, cache: CacheStorage, user: UserDTO) -> None:
    response = await client.post(
        f"/otp/send?action={UserAction.recover_password}&email={user.email}",
    )
    assert response.status_code == status.HTTP_200_OK

    await cache.get(f"otp:users:{user.id}")


async def test_send_otp_recover_password_not_exists(client: AsyncClient, cache: CacheStorage, user: UserDTO) -> None:
    response = await client.post(
        f"/otp/send?action={UserAction.recover_password}&email={faker.email()}",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_send_otp_telegram(
    client: AsyncClient, cache: CacheStorage, user_tg: UserDTO, user_tg_token: TokenResponse
) -> None:
    response = await client.post(
        f"/otp/send?action={UserAction.change_password}",
        headers={"Authorization": f"Bearer {user_tg_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    await cache.get(f"otp:users:{user_tg.id}")
