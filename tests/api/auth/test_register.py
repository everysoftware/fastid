import pytest
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from fastid.database.exceptions import NoResultFoundError
from fastid.database.uow import SQLAlchemyUOW
from fastid.webhooks.models import Webhook
from fastid.webhooks.repositories import WebhookEventWebhookIDSpecification
from tests.mocks import USER_CREATE


async def test_register(client: AsyncClient, webhook_registration: Webhook, uow: SQLAlchemyUOW) -> None:
    response = await client.post("/register", json=USER_CREATE.model_dump(mode="json"))
    assert response.status_code == status.HTTP_201_CREATED
    user = UserDTO.model_validate_json(response.content)

    assert user.first_name == USER_CREATE.first_name
    assert user.last_name == USER_CREATE.last_name
    assert user.email == USER_CREATE.email

    try:
        await uow.webhook_events.find(WebhookEventWebhookIDSpecification(webhook_registration.id))
    except NoResultFoundError:
        pytest.fail("No webhook event created")


async def test_register_existent(client: AsyncClient, user: UserDTO) -> None:
    response = await client.post("/register", json=USER_CREATE.model_dump(mode="json"))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
