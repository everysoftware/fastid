from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.dependencies import vt_transport
from fastid.auth.schemas import UserDTO


async def test_delete_user(client: AsyncClient, user: UserDTO, user_token: TokenResponse, verify_token: str) -> None:
    client.cookies.set(vt_transport.name, verify_token)
    response = await client.delete(
        "/users/me",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    client.cookies.delete(vt_transport.name)
    assert response.status_code == status.HTTP_200_OK
    UserDTO.model_validate_json(response.content)


async def test_delete_user_not_verified(client: AsyncClient, user: UserDTO, user_token: TokenResponse) -> None:
    response = await client.delete(
        "/users/me",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
