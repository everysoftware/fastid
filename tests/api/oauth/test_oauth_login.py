from urllib.parse import parse_qs, urlsplit

import pytest
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import TokenResponse
from fastid.database.uow import SQLAlchemyUOW
from fastid.oauth.repositories import OAuthProviderNameSpecification
from tests.mocks import faker


@pytest.mark.parametrize("provider", ["google", "yandex", "vk", "telegram"])
async def test_oauth_login(client: AsyncClient, user_token: TokenResponse, provider: str) -> None:
    response = await client.get(
        f"/oauth/login/{provider}",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    location = response.headers["location"]
    params = parse_qs(urlsplit(location).query)
    if provider == "telegram":
        assert params["origin"] == ["http://testserver/api/v1/oauth/redirect/telegram"]
    else:
        assert params["redirect_uri"] == [f"http://testserver/api/v1/oauth/callback/{provider}"]


async def test_oauth_login_uses_dynamic_provider_settings(
    client: AsyncClient,
    uow: SQLAlchemyUOW,
    user_token: TokenResponse,
) -> None:
    provider = await uow.oauth_providers.find(OAuthProviderNameSpecification("google"))
    provider.client_id = faker.pystr()
    provider.client_secret = faker.password()
    await uow.commit()

    response = await client.get(
        "/oauth/login/google",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    params = parse_qs(urlsplit(response.headers["location"]).query)
    assert params["client_id"] == [provider.client_id]


async def test_oauth_login_rejects_dynamically_disabled_provider(
    client: AsyncClient,
    uow: SQLAlchemyUOW,
    user_token: TokenResponse,
) -> None:
    provider = await uow.oauth_providers.find(OAuthProviderNameSpecification("google"))
    provider.enabled = False
    await uow.commit()

    response = await client.get(
        "/oauth/login/google",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["type"] == "oauth_provider_disabled"
