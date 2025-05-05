from auth365.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.dependencies import verify_token_transport
from fastid.auth.schemas import UserDTO
from tests.mocks import faker


async def test_update_user_email(
    client: AsyncClient, user: UserDTO, user_token: TokenResponse, verify_token: str
) -> None:
    new_email = faker.email()
    client.cookies.set(verify_token_transport.name, verify_token)
    response = await client.patch(
        "/users/me/email",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
        json={"new_email": new_email},
    )
    client.cookies.delete(verify_token_transport.name)
    assert response.status_code == status.HTTP_200_OK
    user = UserDTO.model_validate_json(response.content)
    assert user.email == new_email


async def test_update_user_email_already_exists(
    client: AsyncClient, user: UserDTO, user_token: TokenResponse, user_tg: UserDTO, verify_token: str
) -> None:
    new_email = user_tg.email
    client.cookies.set(verify_token_transport.name, verify_token)
    response = await client.patch(
        "/users/me/email",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
        json={"new_email": new_email},
    )
    client.cookies.delete(verify_token_transport.name)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_update_user_email_not_verified(client: AsyncClient, user: UserDTO, user_token: TokenResponse) -> None:
    new_email = faker.email()
    response = await client.patch(
        "/users/me/email",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
        json={"new_email": new_email},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
