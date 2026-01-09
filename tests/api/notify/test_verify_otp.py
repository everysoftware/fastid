from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from fastid.cache.storage import CacheStorage
from fastid.notify.schemas import UserAction
from fastid.security.crypto import generate_otp


async def test_verify_otp(client: AsyncClient, cache: CacheStorage, user: UserDTO, user_token: TokenResponse) -> None:
    code = generate_otp()
    await cache.set(f"otp:users:{user.id}", code)

    response = await client.post(
        "/otp/verify",
        json={
            "action": UserAction.change_password,
            "code": code,
        },
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["verify_token"] is not None


async def test_verify_otp_not_exists(
    client: AsyncClient, cache: CacheStorage, user: UserDTO, user_token: TokenResponse
) -> None:
    code = generate_otp()
    response = await client.post(
        "/otp/verify",
        json={
            "action": UserAction.change_password,
            "code": code,
        },
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_verify_otp_wrong_code(
    client: AsyncClient, cache: CacheStorage, user: UserDTO, user_token: TokenResponse
) -> None:
    code = generate_otp()
    fake_code = generate_otp()
    await cache.set(f"otp:users:{user.id}", code)
    response = await client.post(
        "/otp/verify",
        json={
            "action": UserAction.change_password,
            "code": fake_code,
        },
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
