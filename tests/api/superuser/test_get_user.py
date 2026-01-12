from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from fastid.database.utils import uuid


async def test_get_user(client: AsyncClient, user_su: UserDTO, user_su_token: TokenResponse) -> None:
    response = await client.get(
        f"/users/{user_su.id}",
        headers={"Authorization": f"Bearer {user_su_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    user = UserDTO.model_validate_json(response.content)
    assert user == user_su


async def test_get_user_not_su(client: AsyncClient, user: UserDTO, user_token: TokenResponse) -> None:
    response = await client.get(f"/users/{user.id}", headers={"Authorization": f"Bearer {user_token.access_token}"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_get_user_not_exists(client: AsyncClient, user_su_token: TokenResponse) -> None:
    response = await client.get(f"/users/{uuid()}", headers={"Authorization": f"Bearer {user_su_token.access_token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
