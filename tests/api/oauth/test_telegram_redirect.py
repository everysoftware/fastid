from unittest.mock import AsyncMock, patch

from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import TokenResponse
from tests import mocks


async def test_telegram_redirect(client: AsyncClient, user_token: TokenResponse) -> None:
    widget_mock = AsyncMock(return_value=mocks.TELEGRAM_WIDGET)
    with (
        patch("fastid.integrations.telegram.login.TelegramLoginWidget.widget_data", new=widget_mock),
    ):
        response = await client.get(
            "/oauth/redirect/telegram",
            headers={"Authorization": f"Bearer {user_token.access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
