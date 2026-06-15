from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import OpenID, TokenResponse, UserDTO
from fastid.integrations.schemas import UserinfoResponse
from tests import mocks


@pytest.mark.parametrize(("provider", "openid"), [("google", mocks.GOOGLE_OPENID), ("yandex", mocks.YANDEX_OPENID)])
async def test_oauth_callback_authorize(client: AsyncClient, provider: str, openid: OpenID) -> None:
    params = mocks.OAUTH_CALLBACK.model_dump(mode="json", exclude_unset=True)
    authorize_mock = AsyncMock(return_value=mocks.LOGIN_RESPONSE)
    userinfo_mock = AsyncMock(return_value=openid)
    with (
        patch("fastid.integrations.base.oauth.OAuth2Client.login", new=authorize_mock),
        patch("fastid.integrations.base.oauth.OAuth2Client.userinfo", new=userinfo_mock),
    ):
        response = await client.get(f"/oauth/callback/{provider}", params=params)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT


@pytest.mark.parametrize(("provider", "openid"), [("google", mocks.GOOGLE_OPENID), ("yandex", mocks.YANDEX_OPENID)])
async def test_oauth_callback_authorize_email_exists(
    client: AsyncClient,
    user: UserDTO,
    provider: str,
    openid: UserinfoResponse,
) -> None:
    openid.userinfo.email = user.email

    params = mocks.OAUTH_CALLBACK.model_dump(mode="json", exclude_unset=True)
    authorize_mock = AsyncMock(return_value=mocks.LOGIN_RESPONSE)
    userinfo_mock = AsyncMock(return_value=openid)
    with (
        patch("fastid.integrations.base.oauth.OAuth2Client.login", new=authorize_mock),
        patch("fastid.integrations.base.oauth.OAuth2Client.userinfo", new=userinfo_mock),
    ):
        response = await client.get(f"/oauth/callback/{provider}", params=params)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT


@pytest.mark.parametrize(("provider", "openid"), [("google", mocks.GOOGLE_OPENID), ("yandex", mocks.YANDEX_OPENID)])
async def test_oauth_callback_connect(
    client: AsyncClient,
    user_token: TokenResponse,
    provider: str,
    openid: OpenID,
) -> None:
    params = mocks.OAUTH_CALLBACK.model_dump(mode="json", exclude_unset=True)
    authorize_mock = AsyncMock(return_value=mocks.LOGIN_RESPONSE)
    userinfo_mock = AsyncMock(return_value=openid)
    with (
        patch("fastid.integrations.base.oauth.OAuth2Client.login", new=authorize_mock),
        patch("fastid.integrations.base.oauth.OAuth2Client.userinfo", new=userinfo_mock),
    ):
        response = await client.get(
            f"/oauth/callback/{provider}",
            headers={"Authorization": f"Bearer {user_token.access_token}"},
            params=params,
        )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT


@pytest.mark.parametrize(("provider", "openid"), [("google", mocks.GOOGLE_OPENID), ("yandex", mocks.YANDEX_OPENID)])
async def test_oauth_callback_double_connect(
    client: AsyncClient,
    user_token: TokenResponse,
    provider: str,
    openid: OpenID,
) -> None:
    params = mocks.OAUTH_CALLBACK.model_dump(mode="json", exclude_unset=True)
    authorize_mock = AsyncMock(return_value=mocks.LOGIN_RESPONSE)
    userinfo_mock = AsyncMock(return_value=openid)
    with (
        patch("fastid.integrations.base.oauth.OAuth2Client.login", new=authorize_mock),
        patch("fastid.integrations.base.oauth.OAuth2Client.userinfo", new=userinfo_mock),
    ):
        response = await client.get(
            f"/oauth/callback/{provider}",
            headers={"Authorization": f"Bearer {user_token.access_token}"},
            params=params,
        )
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

        response = await client.get(
            f"/oauth/callback/{provider}",
            headers={"Authorization": f"Bearer {user_token.access_token}"},
            params=params,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_telegram_callback_register(client: AsyncClient) -> None:
    params = mocks.TELEGRAM_CALLBACK.model_dump(mode="json", exclude_unset=True)
    userinfo_mock = AsyncMock(return_value=mocks.TELEGRAM_OPENID)
    with (
        patch("fastid.integrations.telegram.login.TelegramLoginWidget.verify", new=userinfo_mock),
    ):
        response = await client.get(
            "/oauth/callback/telegram",
            params=params,
        )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT


async def test_telegram_callback_connect(client: AsyncClient, user_token: TokenResponse) -> None:
    params = mocks.TELEGRAM_CALLBACK.model_dump(mode="json", exclude_unset=True)
    userinfo_mock = AsyncMock(return_value=mocks.TELEGRAM_OPENID)
    with (
        patch("fastid.integrations.telegram.login.TelegramLoginWidget.verify", new=userinfo_mock),
    ):
        response = await client.get(
            "/oauth/callback/telegram",
            headers={"Authorization": f"Bearer {user_token.access_token}"},
            params=params,
        )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
