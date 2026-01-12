from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.dependencies import vt_transport
from fastid.auth.schemas import UserDTO
from tests.mocks import faker


async def test_update_user_password(
    client: AsyncClient,
    user: UserDTO,
    user_token: TokenResponse,
    verify_token: str,
) -> None:
    new_password = faker.password()
    client.cookies.set(vt_transport.name, verify_token)
    response = await client.patch(
        "/users/me/password",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
        json={"password": new_password},
    )
    client.cookies.delete(vt_transport.name)
    assert response.status_code == status.HTTP_200_OK
    UserDTO.model_validate_json(response.content)


async def test_update_user_password_not_verified(client: AsyncClient, user: UserDTO, user_token: TokenResponse) -> None:
    new_password = faker.password()
    response = await client.patch(
        "/users/me/password",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
        json={"password": new_password},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
