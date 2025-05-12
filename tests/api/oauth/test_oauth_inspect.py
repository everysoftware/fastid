import pytest
from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.oauth.schemas import InspectProviderResponse


@pytest.mark.parametrize("provider", ["google", "yandex", "telegram"])
async def test_oauth_inspect(client: AsyncClient, user_token: TokenResponse, provider: str) -> None:
    response = await client.get(
        f"/oauth/inspect/{provider}",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    InspectProviderResponse.model_validate_json(response.content)
