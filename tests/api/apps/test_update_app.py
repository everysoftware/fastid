from httpx import AsyncClient
from starlette import status

from fastid.apps.schemas import AppDTO
from fastid.auth.schemas import TokenResponse
from fastid.database.utils import uuid
from tests import mocks


async def test_update_app(client: AsyncClient, oauth_app: AppDTO, user_su_token: TokenResponse) -> None:
    response = await client.patch(
        f"/apps/{oauth_app.id}",
        json=mocks.APP_UPDATE.model_dump(mode="json", exclude_unset=True),
        headers={"Authorization": f"Bearer {user_su_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    app = AppDTO.model_validate_json(response.content)
    assert app.name == mocks.APP_UPDATE.name


async def test_update_app_not_exists(client: AsyncClient, oauth_app: AppDTO, user_su_token: TokenResponse) -> None:
    response = await client.patch(
        f"/apps/{uuid()}",
        json=mocks.APP_UPDATE.model_dump(mode="json", exclude_unset=True),
        headers={"Authorization": f"Bearer {user_su_token.access_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_update_app_not_su(client: AsyncClient, oauth_app: AppDTO, user_token: TokenResponse) -> None:
    response = await client.patch(
        f"/apps/{oauth_app.id}",
        json=mocks.APP_UPDATE.model_dump(mode="json", exclude_unset=True),
        headers={"Authorization": f"Bearer {user_token.access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_cold_fill_and_mutation_share_single_connection(oauth_app: AppDTO) -> None:
    import asyncio

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from fastid.apps.schemas import AppUpdate
    from fastid.apps.use_cases import AppUseCases
    from fastid.auth.grants import ClientCredentialsGrant
    from fastid.database.uow import SQLAlchemyUOW
    from tests.dependencies import get_test_cache, test_engine

    rotated = "fixture-rotated-secret"
    engine = create_async_engine(test_engine.url, pool_size=1, max_overflow=0, pool_timeout=0.5)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    cache = get_test_cache()
    task = None
    try:
        async with SQLAlchemyUOW(factory) as uow:
            app = await uow.apps.get(oauth_app.id)
            grant = ClientCredentialsGrant(SQLAlchemyUOW(factory), cache, "http://testserver")
            task = asyncio.create_task(grant.validate_client(oauth_app.client_id))
            # Wait until the cold fill holds Redis and is waiting for PostgreSQL.
            async with asyncio.timeout(2):
                while not await cache.client.exists(f"lock:apps:{oauth_app.client_id}"):  # noqa: ASYNC110 - observe real Redis lease
                    await asyncio.sleep(0.001)
            await AppUseCases(uow, cache).update(app, AppUpdate(client_secret=rotated))
            await task
        snapshot = await grant.authenticate_client(oauth_app.client_id, rotated)
        assert snapshot.id == oauth_app.id
    finally:
        if task is not None and not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await engine.dispose()
