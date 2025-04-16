import pytest
from auth365.schemas import TokenResponse
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette import status

from app.auth.schemas import UserDTO
from app.logging.dependencies import provider
from tests.mocks import USER_CREATE
from tests.utils.db import delete_all

logger = provider.logger(__name__)


@pytest.fixture(autouse=True)
async def _reset_db(engine: AsyncEngine) -> None:
    await delete_all(engine)


@pytest.fixture(autouse=True)
async def _reset_redis(redis_client: Redis) -> None:
    await redis_client.flushdb()


@pytest.fixture
async def user(client: AsyncClient) -> UserDTO:
    response = await client.post("/register", json=USER_CREATE.model_dump(mode="json"))
    assert response.status_code == status.HTTP_201_CREATED
    return UserDTO.model_validate_json(response.content)


@pytest.fixture
async def token(user: UserDTO, client: AsyncClient) -> TokenResponse:
    response = await client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": user.email,
            "password": USER_CREATE.password,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    return TokenResponse.model_validate_json(response.content)
