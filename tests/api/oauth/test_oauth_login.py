import pytest
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import TokenResponse


@pytest.mark.parametrize("provider", ["google", "yandex", "vk", "telegram"])
async def test_oauth_login(client: AsyncClient, user_token: TokenResponse, provider: str) -> None:
    response = await client.get(
        f"/oauth/login/{provider}",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
