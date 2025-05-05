from auth365.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from fastid.database.schemas import PageDTO


async def test_get_users(client: AsyncClient, user_su: UserDTO, user_su_token: TokenResponse) -> None:
    response = await client.get("/users/", headers={"Authorization": f"Bearer {user_su_token.access_token}"})
    assert response.status_code == status.HTTP_200_OK
    page = PageDTO[UserDTO].model_validate_json(response.content)
    assert page.total == 1
    assert page.items[0] == user_su


async def test_get_users_not_su(client: AsyncClient, user: UserDTO, user_token: TokenResponse) -> None:
    response = await client.get("/users/", headers={"Authorization": f"Bearer {user_token.access_token}"})
    assert response.status_code == status.HTTP_403_FORBIDDEN
