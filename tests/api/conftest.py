from typing import cast

import pytest
from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette import status

from fastid.apps.schemas import AppDTO
from fastid.auth.schemas import UserDTO
from fastid.cache.storage import CacheStorage
from fastid.core.dependencies import log_provider
from fastid.database.uow import SQLAlchemyUOW
from fastid.notify.schemas import UnsafeAction
from fastid.security.crypto import generate_otp
from tests import mocks
from tests.utils.auth import authorize_password_grant, register_user
from tests.utils.db import delete_all

logger = log_provider.logger(__name__)


@pytest.fixture(autouse=True)
async def _reset_db(engine: AsyncEngine) -> None:
    await delete_all(engine)


@pytest.fixture(autouse=True)
async def _reset_redis(redis_client: Redis) -> None:
    await redis_client.flushdb()


@pytest.fixture
async def user(client: AsyncClient) -> UserDTO:
    response = await client.post("/register", json=mocks.USER_CREATE.model_dump(mode="json"))
    assert response.status_code == status.HTTP_201_CREATED
    return UserDTO.model_validate_json(response.content)


@pytest.fixture
async def user_su(uow: SQLAlchemyUOW) -> UserDTO:
    return await register_user(uow, mocks.USER_SU_RECORD)


@pytest.fixture
async def user_tg(uow: SQLAlchemyUOW) -> UserDTO:
    return await register_user(uow, mocks.USER_TG_RECORD)


@pytest.fixture
async def user_token(user: UserDTO, client: AsyncClient) -> TokenResponse:
    assert user.email is not None
    return await authorize_password_grant(client, user.email, mocks.USER_CREATE.password)


@pytest.fixture
async def user_su_token(user_su: UserDTO, client: AsyncClient) -> TokenResponse:
    assert user_su.email is not None
    return await authorize_password_grant(client, user_su.email, mocks.USER_SU_CREATE.password)


@pytest.fixture
async def user_tg_token(user_tg: UserDTO, client: AsyncClient) -> TokenResponse:
    assert user_tg.email is not None
    return await authorize_password_grant(client, user_tg.email, mocks.USER_TG_CREATE.password)


@pytest.fixture
async def verify_token(client: AsyncClient, cache: CacheStorage, user: UserDTO, user_token: TokenResponse) -> str:
    code = generate_otp()
    await cache.set(f"otp:users:{user.id}", code)

    response = await client.post(
        "/otp/verify",
        json={
            "action": UnsafeAction.change_password,
            "code": code,
        },
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    return cast(str, content["verify_token"])


@pytest.fixture
async def oauth_app(client: AsyncClient, user_su_token: TokenResponse) -> AppDTO:
    response = await client.post(
        "/apps",
        json=mocks.APP_CREATE.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_su_token.access_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    return AppDTO.model_validate_json(response.content)
