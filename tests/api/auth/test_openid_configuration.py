from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import JWKS, DiscoveryDocument


async def test_openid_configuration(frontend_client: AsyncClient) -> None:
    response = await frontend_client.get("/.well-known/openid-configuration")
    assert response.status_code == status.HTTP_200_OK
    DiscoveryDocument.model_validate_json(response.content)


async def test_jwks(frontend_client: AsyncClient) -> None:
    response = await frontend_client.get("/.well-known/jwks.json")
    assert response.status_code == status.HTTP_200_OK
    JWKS.model_validate_json(response.content)
