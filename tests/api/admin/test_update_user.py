from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from fastid.database.utils import uuid
from tests import mocks


async def test_update_user(client: AsyncClient, user_su: UserDTO, user_su_token: TokenResponse) -> None:
    response = await client.patch(
        f"/users/{user_su.id}",
        headers={"Authorization": f"Bearer {user_su_token.access_token}"},
        json=mocks.USER_UPDATE.model_dump(mode="json", exclude_unset=True),
    )
    assert response.status_code == status.HTTP_200_OK
    user = UserDTO.model_validate_json(response.content)
    assert user.first_name == mocks.USER_UPDATE.first_name
    assert user.last_name == mocks.USER_UPDATE.last_name


async def test_update_user_not_su(client: AsyncClient, user: UserDTO, user_token: TokenResponse) -> None:
    response = await client.patch(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
        json=mocks.USER_UPDATE.model_dump(mode="json", exclude_unset=True),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_update_user_not_exists(client: AsyncClient, user_su_token: TokenResponse) -> None:
    response = await client.patch(
        f"/users/{uuid()}",
        headers={"Authorization": f"Bearer {user_su_token.access_token}"},
        json=mocks.USER_UPDATE.model_dump(mode="json", exclude_unset=True),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
