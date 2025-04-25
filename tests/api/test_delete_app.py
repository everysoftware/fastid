from auth365.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from app.apps.schemas import AppDTO


async def test_delete_app(client: AsyncClient, oauth_app: AppDTO, user_su_token: TokenResponse) -> None:
    response = await client.delete(
        f"/apps/{oauth_app.id}",
        headers={"Authorization": f"Bearer {user_su_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    AppDTO.model_validate_json(response.content)


async def test_delete_app_not_su(client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse) -> None:
    response = await client.delete(
        f"/apps/{oauth_app.id}",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
