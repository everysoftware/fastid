from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.apps.schemas import AppDTO
from fastid.database.utils import uuid


async def test_get_app(client: AsyncClient, oauth_app: AppDTO, user_su_token: TokenResponse) -> None:
    response = await client.get(
        f"/apps/{oauth_app.id}",
        headers={"Authorization": f"Bearer {user_su_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    app = AppDTO.model_validate_json(response.content)
    assert app == oauth_app


async def test_get_app_not_exists(client: AsyncClient, oauth_app: AppDTO, user_su_token: TokenResponse) -> None:
    response = await client.get(
        f"/apps/{uuid()}",
        headers={"Authorization": f"Bearer {user_su_token.access_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_app_not_su(client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse) -> None:
    response = await client.get(
        f"/apps/{oauth_app.id}",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
