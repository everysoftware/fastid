import pytest
from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.dependencies import vt_transport
from fastid.auth.schemas import UserDTO
from fastid.cache.storage import CacheStorage
from fastid.database.exceptions import NoResultFoundError
from fastid.database.uow import SQLAlchemyUOW
from fastid.security.crypto import generate_otp
from fastid.webhooks.models import Webhook
from fastid.webhooks.repositories import WebhookEventWebhookIDSpecification
from tests.mocks import faker


async def test_update_user_email(  # noqa: PLR0913
    client: AsyncClient,
    cache: CacheStorage,
    user: UserDTO,
    user_token: TokenResponse,
    verify_token: str,
    webhook_change_email: Webhook,
    uow: SQLAlchemyUOW,
) -> None:
    code = generate_otp()
    await cache.set(f"otp:users:{user.id}", code)

    new_email = faker.email()
    client.cookies.set(vt_transport.name, verify_token)
    response = await client.patch(
        "/users/me/email",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
        json={"new_email": new_email, "code": code},
    )
    client.cookies.delete(vt_transport.name)
    assert response.status_code == status.HTTP_200_OK
    user = UserDTO.model_validate_json(response.content)
    assert user.email == new_email

    try:
        await uow.webhook_events.find(WebhookEventWebhookIDSpecification(webhook_change_email.id))
    except NoResultFoundError:
        pytest.fail("No webhook event created")


async def test_update_user_email_already_exists(  # noqa: PLR0913
    client: AsyncClient,
    cache: CacheStorage,
    user: UserDTO,
    user_token: TokenResponse,
    user_tg: UserDTO,
    verify_token: str,
) -> None:
    code = generate_otp()
    await cache.set(f"otp:users:{user.id}", code)

    new_email = user_tg.email
    client.cookies.set(vt_transport.name, verify_token)
    response = await client.patch(
        "/users/me/email",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
        json={"new_email": new_email, "code": code},
    )
    client.cookies.delete(vt_transport.name)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_update_user_email_not_verified(
    client: AsyncClient,
    cache: CacheStorage,
    user: UserDTO,
    user_token: TokenResponse,
) -> None:
    code = generate_otp()
    await cache.set(f"otp:users:{user.id}", code)

    new_email = faker.email()
    response = await client.patch(
        "/users/me/email",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
        json={"new_email": new_email, "code": code},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
