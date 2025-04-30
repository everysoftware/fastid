from auth365.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.apps.schemas import AppDTO
from tests import mocks


async def test_update_app(client: AsyncClient, oauth_app: AppDTO, user_su_token: TokenResponse) -> None:
    response = await client.patch(
        f"/apps/{oauth_app.id}",
        json=mocks.APP_UPDATE.model_dump(mode="json", exclude_unset=True),
        headers={"Authorization": f"Bearer {user_su_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    app = AppDTO.model_validate_json(response.content)
    assert app.name == mocks.APP_UPDATE.name


async def test_update_app_not_su(client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse) -> None:
    response = await client.patch(
        f"/apps/{oauth_app.id}",
        json=mocks.APP_UPDATE.model_dump(mode="json", exclude_unset=True),
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
