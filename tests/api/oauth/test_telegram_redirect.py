from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status


async def test_telegram_redirect(client: AsyncClient, user_token: TokenResponse) -> None:
    response = await client.get(
        "/oauth/redirect/telegram",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
