from auth365.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO


async def test_revoke_su(client: AsyncClient, user_su: UserDTO, user_su_token: TokenResponse) -> None:
    response = await client.post(
        f"/users/{user_su.id}/revoke",
        headers={"Authorization": f"Bearer {user_su_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    actual_user = UserDTO.model_validate_json(response.content)
    assert not actual_user.is_superuser


async def test_revoke_su_not_su(client: AsyncClient, user: UserDTO, user_token: TokenResponse) -> None:
    response = await client.post(
        f"/users/{user.id}/revoke",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
