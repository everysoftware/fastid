from auth365.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.dependencies import cookie_transport


async def test_logout(client: AsyncClient, user_token: TokenResponse) -> None:
    assert user_token.access_token is not None
    client.cookies.set(cookie_transport.name, user_token.access_token)
    response = await client.get("/logout")
    client.cookies.delete(cookie_transport.name)
    assert response.status_code == status.HTTP_200_OK
    assert f'{cookie_transport.name}=""' in response.headers["Set-Cookie"]
