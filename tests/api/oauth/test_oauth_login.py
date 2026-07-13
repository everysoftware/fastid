from urllib.parse import parse_qs, urlsplit

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
    location = response.headers["location"]
    params = parse_qs(urlsplit(location).query)
    if provider == "telegram":
        assert params["origin"] == ["http://testserver/api/v1/oauth/redirect/telegram"]
    else:
        assert params["redirect_uri"] == [f"http://testserver/api/v1/oauth/callback/{provider}"]
