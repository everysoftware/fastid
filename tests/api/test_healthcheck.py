from fastapi import status
from httpx import AsyncClient


async def test_readiness(client: AsyncClient) -> None:
    response = await client.get("/readiness")
    response.raise_for_status()
    assert response.json() == {"status": "ok"}


async def test_liveness(client: AsyncClient) -> None:
    response = await client.get("/liveness")
    response.raise_for_status()
    assert response.json() == {"db": True, "cache": True}


async def test_exception(client: AsyncClient) -> None:
    response = await client.get("/exc")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert content["msg"] == "Test error"
    assert content["type"] == "test_error"
