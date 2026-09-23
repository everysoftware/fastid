from httpx import AsyncClient


async def test_readiness(core_client: AsyncClient) -> None:
    response = await core_client.get("/readiness")
    response.raise_for_status()
    assert response.json() == {"status": "ok"}


async def test_liveness(core_client: AsyncClient) -> None:
    response = await core_client.get("/liveness")
    response.raise_for_status()
    assert response.json() == {"db": True, "cache": True}
