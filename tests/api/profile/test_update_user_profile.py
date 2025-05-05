from auth365.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from tests import mocks


async def test_update_user_profile(client: AsyncClient, user: UserDTO, user_token: TokenResponse) -> None:
    response = await client.patch(
        "/users/me/profile",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
        json=mocks.USER_UPDATE.model_dump(mode="json", exclude_unset=True),
    )
    assert response.status_code == status.HTTP_200_OK
    user = UserDTO.model_validate_json(response.content)
    assert user.first_name == mocks.USER_UPDATE.first_name
    assert user.last_name == mocks.USER_UPDATE.last_name
