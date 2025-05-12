from unittest.mock import AsyncMock, patch

import pytest
from fastlink.schemas import OpenID, TokenResponse
from httpx import AsyncClient
from starlette import status

from tests import mocks


@pytest.mark.parametrize(("provider", "openid"), [("google", mocks.GOOGLE_OPENID), ("yandex", mocks.YANDEX_OPENID)])
async def test_oauth_callback_register(client: AsyncClient, provider: str, openid: OpenID) -> None:
    params = mocks.OAUTH_CALLBACK.model_dump(mode="json", exclude_unset=True)
    authorize_mock = AsyncMock(return_value=mocks.OAUTH_TOKEN_RESPONSE)
    userinfo_mock = AsyncMock(return_value=openid)
    with (
        patch("auth365.providers.base.HttpxClient.authorize", new=authorize_mock),
        patch("auth365.providers.base.HttpxClient.userinfo", new=userinfo_mock),
    ):
        response = await client.get(f"/oauth/callback/{provider}", params=params)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT


@pytest.mark.parametrize(("provider", "openid"), [("google", mocks.GOOGLE_OPENID), ("yandex", mocks.YANDEX_OPENID)])
async def test_oauth_callback_connect(
    client: AsyncClient, user_token: TokenResponse, provider: str, openid: OpenID
) -> None:
    params = mocks.OAUTH_CALLBACK.model_dump(mode="json", exclude_unset=True)
    authorize_mock = AsyncMock(return_value=mocks.OAUTH_TOKEN_RESPONSE)
    userinfo_mock = AsyncMock(return_value=openid)
    with (
        patch("auth365.providers.base.HttpxClient.authorize", new=authorize_mock),
        patch("auth365.providers.base.HttpxClient.userinfo", new=userinfo_mock),
    ):
        response = await client.get(
            f"/oauth/callback/{provider}", headers={"Authorization": f"Bearer {user_token.access_token}"}, params=params
        )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT


async def test_telegram_callback_register(client: AsyncClient) -> None:
    params = mocks.TELEGRAM_CALLBACK.model_dump(mode="json", exclude_unset=True)
    authorize_mock = AsyncMock(return_value=mocks.OAUTH_TOKEN_RESPONSE)
    userinfo_mock = AsyncMock(return_value=mocks.TELEGRAM_OPENID)
    with (
        patch("auth365.providers.telegram.TelegramImplicitOAuth.authorize", new=authorize_mock),
        patch("auth365.providers.telegram.TelegramImplicitOAuth.userinfo", new=userinfo_mock),
    ):
        response = await client.get(
            "/oauth/callback/telegram",
            params=params,
        )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT


async def test_telegram_callback_connect(client: AsyncClient, user_token: TokenResponse) -> None:
    params = mocks.TELEGRAM_CALLBACK.model_dump(mode="json", exclude_unset=True)
    authorize_mock = AsyncMock(return_value=mocks.OAUTH_TOKEN_RESPONSE)
    userinfo_mock = AsyncMock(return_value=mocks.TELEGRAM_OPENID)
    with (
        patch("auth365.providers.telegram.TelegramImplicitOAuth.authorize", new=authorize_mock),
        patch("auth365.providers.telegram.TelegramImplicitOAuth.userinfo", new=userinfo_mock),
    ):
        response = await client.get(
            "/oauth/callback/telegram",
            headers={"Authorization": f"Bearer {user_token.access_token}"},
            params=params,
        )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
