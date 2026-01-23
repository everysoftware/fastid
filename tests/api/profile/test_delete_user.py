import pytest
from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.dependencies import vt_transport
from fastid.auth.schemas import UserDTO
from fastid.database.exceptions import NoResultFoundError
from fastid.database.uow import SQLAlchemyUOW
from fastid.webhooks.models import Webhook
from fastid.webhooks.repositories import WebhookEventWebhookIDSpecification


async def test_delete_user(  # noqa: PLR0913
    client: AsyncClient,
    user: UserDTO,
    user_token: TokenResponse,
    verify_token: str,
    webhook_delete: Webhook,
    uow: SQLAlchemyUOW,
) -> None:
    client.cookies.set(vt_transport.name, verify_token)
    response = await client.delete(
        "/users/me",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    client.cookies.delete(vt_transport.name)
    assert response.status_code == status.HTTP_200_OK
    UserDTO.model_validate_json(response.content)

    try:
        await uow.webhook_events.find(WebhookEventWebhookIDSpecification(webhook_delete.id))
    except NoResultFoundError:
        pytest.fail("No webhook event created")


async def test_delete_user_not_verified(client: AsyncClient, user: UserDTO, user_token: TokenResponse) -> None:
    response = await client.delete(
        "/users/me",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
