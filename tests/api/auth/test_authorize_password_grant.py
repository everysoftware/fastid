import jwt
import pytest
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from fastid.core.config import core_settings
from fastid.database.exceptions import NoResultFoundError
from fastid.database.uow import SQLAlchemyUOW
from fastid.webhooks.models import Webhook
from fastid.webhooks.repositories import WebhookEventWebhookIDSpecification
from tests import mocks
from tests.mocks import faker
from tests.utils.auth import (
    authorize_password_grant,
)


async def test_authorize_password_grant(
    client: AsyncClient, user: UserDTO, webhook_login: Webhook, uow: SQLAlchemyUOW
) -> None:
    assert user.email is not None
    token = await authorize_password_grant(client, user.email, mocks.USER_CREATE.password)
    assert token.access_token is not None
    assert token.refresh_token is not None

    try:
        await uow.webhook_events.find(WebhookEventWebhookIDSpecification(webhook_login.id))
    except NoResultFoundError:
        pytest.fail("No webhook event created")


async def test_dynamic_server_url_is_used_as_jwt_issuer(
    client: AsyncClient,
    user: UserDTO,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(core_settings, "public_url", None)
    assert user.email is not None

    token = await authorize_password_grant(client, user.email, mocks.USER_CREATE.password)
    assert token.access_token is not None
    claims = jwt.decode(token.access_token, options={"verify_signature": False})

    assert claims["iss"] == "http://testserver"


async def test_configured_public_url_is_used_as_jwt_issuer(
    client: AsyncClient,
    user: UserDTO,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server_url = "https://configured.example.com"
    monkeypatch.setattr(core_settings, "public_url", server_url)
    assert user.email is not None

    token = await authorize_password_grant(client, user.email, mocks.USER_CREATE.password)
    assert token.access_token is not None
    claims = jwt.decode(token.access_token, options={"verify_signature": False})

    assert claims["iss"] == server_url


async def test_authorize_password_grant_not_exists(client: AsyncClient) -> None:
    response = await client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": faker.email(),
            "password": mocks.USER_CREATE.password,
            "scope": "offline_access",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_authorize_password_grant_wrong_password(client: AsyncClient, user: UserDTO) -> None:
    response = await client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": user.email,
            "password": faker.password(),
            "scope": "offline_access",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
