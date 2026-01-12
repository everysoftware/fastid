import pytest
from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from tests.mocks import PUSH_NOTIFICATION_REQUEST, PUSH_NOTIFICATION_REQUEST_FAKE_TEMPLATE


async def test_send_telegram(client: AsyncClient, user_tg_token: TokenResponse) -> None:
    response = await client.post(
        "/telegram/send",
        headers={"Authorization": f"Bearer {user_tg_token.access_token}"},
        json=PUSH_NOTIFICATION_REQUEST.model_dump(mode="json"),
    )
    assert response.status_code == status.HTTP_200_OK


async def test_send_telegram_fake_template(client: AsyncClient, user_tg_token: TokenResponse) -> None:
    with pytest.raises(RuntimeError):
        await client.post(
            "/telegram/send",
            headers={"Authorization": f"Bearer {user_tg_token.access_token}"},
            json=PUSH_NOTIFICATION_REQUEST_FAKE_TEMPLATE.model_dump(mode="json"),
        )


async def test_send_telegram_no_telegram_id(client: AsyncClient, user_token: TokenResponse) -> None:
    with pytest.raises(RuntimeError):
        await client.post(
            "/telegram/send",
            headers={"Authorization": f"Bearer {user_token.access_token}"},
            json=PUSH_NOTIFICATION_REQUEST.model_dump(mode="json"),
        )
