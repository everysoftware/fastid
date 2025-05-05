from auth365.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.apps.schemas import AppDTO
from tests import mocks


async def test_create_app(client: AsyncClient, user_su_token: TokenResponse) -> None:
    response = await client.post(
        "/apps",
        json=mocks.APP_CREATE.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_su_token.access_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    AppDTO.model_validate_json(response.content)


async def test_create_app_not_su(client: AsyncClient, user_token: TokenResponse) -> None:
    response = await client.post(
        "/apps",
        json=mocks.APP_CREATE.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
