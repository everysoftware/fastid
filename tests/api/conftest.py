import pytest
from auth365.schemas import TokenResponse
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette import status

from app.apps.schemas import AppDTO
from app.auth.models import User
from app.auth.schemas import UserDTO
from app.db.uow import IUnitOfWork
from app.logging.dependencies import provider
from tests.mocks import APP_CREATE, USER_CREATE, USER_SU_CREATE, USER_SU_RECORD
from tests.utils.auth import authorize_password_grant
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
async def user_su(uow: IUnitOfWork) -> UserDTO:
    record = User(**USER_SU_RECORD)
    await uow.users.add(record)
    await uow.commit()
    user = UserDTO.model_validate(record)
    user.hashed_password = None
    return user


@pytest.fixture
async def user_token(user: UserDTO, client: AsyncClient) -> TokenResponse:
    assert user.email is not None
    return await authorize_password_grant(client, user.email, USER_CREATE.password)


@pytest.fixture
async def user_su_token(user_su: UserDTO, client: AsyncClient) -> TokenResponse:
    assert user_su.email is not None
    return await authorize_password_grant(client, user_su.email, USER_SU_CREATE.password)


@pytest.fixture
async def oauth_app(client: AsyncClient, user_su_token: TokenResponse) -> AppDTO:
    response = await client.post(
        "/apps",
        json=APP_CREATE.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_su_token.access_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    return AppDTO.model_validate_json(response.content)
