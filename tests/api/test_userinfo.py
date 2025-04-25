from auth365.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from app.auth.schemas import UserDTO


async def test_userinfo(client: AsyncClient, user: UserDTO, user_token: TokenResponse) -> None:
    response = await client.get("/userinfo", headers={"Authorization": f"Bearer {user_token.access_token}"})
    assert response.status_code == status.HTTP_200_OK
    actual_user = UserDTO.model_validate_json(response.content)
    assert actual_user == user


async def test_userinfo_unauthorized(client: AsyncClient, user: UserDTO) -> None:
    response = await client.get("/userinfo")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
