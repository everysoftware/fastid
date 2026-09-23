import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from starlette import status

from fastid.apps.schemas import AppDTO
from fastid.auth.schemas import UserDTO
from fastid.database.exceptions import NoResultFoundError
from fastid.database.uow import SQLAlchemyUOW
from fastid.webhooks.models import WebhookDelivery, WebhookEndpoint, WebhookType
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


async def test_register_enqueues_every_active_webhook_endpoint(
    client: AsyncClient,
    oauth_app: AppDTO,
    uow: SQLAlchemyUOW,
) -> None:
    endpoint_count = 101
    for index in range(endpoint_count):
        await uow.webhook_endpoints.add(
            WebhookEndpoint(
                app_id=oauth_app.id,
                type=WebhookType.user_registration,
                url=f"https://example.com/webhooks/{index}",
            )
        )
    await uow.commit()

    response = await client.post("/register", json=USER_CREATE.model_dump(mode="json"))

    assert response.status_code == status.HTTP_201_CREATED
    delivery_count = await uow.session.scalar(select(func.count()).select_from(WebhookDelivery))
    assert delivery_count == endpoint_count
