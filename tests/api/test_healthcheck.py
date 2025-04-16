from fastapi import status
from httpx import AsyncClient


async def test_hc(client: AsyncClient) -> None:
    response = await client.get("/hc")
    response.raise_for_status()
    assert response.json() == {"status": "ok"}


async def test_exception(client: AsyncClient) -> None:
    response = await client.get("/exc")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert content["msg"] == "Test error"
    assert content["type"] == "test_error"
