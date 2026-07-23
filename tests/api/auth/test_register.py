import pytest
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from fastid.database.exceptions import NoResultFoundError
from fastid.database.uow import SQLAlchemyUOW
from fastid.webhooks.models import WebhookEndpoint
from fastid.webhooks.repositories import WebhookDeliveryEndpointIDSpecification
from tests.mocks import USER_CREATE


async def test_register(client: AsyncClient, webhook_registration: WebhookEndpoint, uow: SQLAlchemyUOW) -> None:
    response = await client.post("/register", json=USER_CREATE.model_dump(mode="json"))
    assert response.status_code == status.HTTP_201_CREATED
    user = UserDTO.model_validate_json(response.content)

    assert user.first_name == USER_CREATE.first_name
    assert user.last_name == USER_CREATE.last_name
    assert user.email == USER_CREATE.email

    try:
        await uow.webhook_deliveries.find(WebhookDeliveryEndpointIDSpecification(webhook_registration.id))
    except NoResultFoundError:
        pytest.fail("No webhook delivery created")


async def test_register_existent(client: AsyncClient, user: UserDTO) -> None:
    response = await client.post("/register", json=USER_CREATE.model_dump(mode="json"))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
