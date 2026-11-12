from typing import Any

import fastapi.dependencies.utils
import jwt
import pytest
from httpx import AsyncClient
from starlette import status

from fastid.apps.schemas import AppDTO
from fastid.auth.schemas import TokenResponse

ROTATED_SECRET = "fixture-rotated-secret"  # noqa: S105 - synthetic test credential


async def issue(client: AsyncClient, app: AppDTO, **changes: Any) -> Any:
    return await client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": app.client_id,
            "client_secret": app.client_secret,
            **changes,
        },
    )


@pytest.mark.parametrize("change", ["secret", "disabled", "client_id", "deleted"])
async def test_cached_client_revoked_after_mutation(
    client: AsyncClient,
    oauth_app: AppDTO,
    user_su_token: TokenResponse,
    change: str,
) -> None:
    assert (await issue(client, oauth_app)).status_code == status.HTTP_200_OK
    headers = {"Authorization": f"Bearer {user_su_token.access_token}"}
    if change == "deleted":
        response = await client.delete(f"/apps/{oauth_app.id}", headers=headers)
    else:
        patch = {
            "secret": {"client_secret": ROTATED_SECRET},
            "disabled": {"is_active": False},
            "client_id": {"client_id": "rotated-client"},
        }[change]
        response = await client.patch(f"/apps/{oauth_app.id}", json=patch, headers=headers)
    assert response.is_success
    assert (await issue(client, oauth_app)).status_code == status.HTTP_401_UNAUTHORIZED
    if change == "secret":
        assert (await issue(client, oauth_app, client_secret=ROTATED_SECRET)).status_code == status.HTTP_200_OK
    if change == "client_id":
        assert (await issue(client, oauth_app, client_id="rotated-client")).status_code == status.HTTP_200_OK


async def test_token_only_resolves_selected_grant(
    client: AsyncClient,
    oauth_app: AppDTO,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = []
    original = fastapi.dependencies.utils.run_in_threadpool

    async def record(func: Any, *args: Any, **kwargs: Any) -> Any:
        calls.append(func.__name__)
        return await original(func, *args, **kwargs)

    monkeypatch.setattr(fastapi.dependencies.utils, "run_in_threadpool", record)
    response = await issue(client, oauth_app)
    assert response.status_code == status.HTTP_200_OK
    assert jwt.get_unverified_header(response.json()["access_token"])["alg"] == "HS256"
    assert not {
        "get_core_settings",
        "get_server_url",
        "get_sender",
        "ClientCredentialsGrant",
        "PasswordGrant",
        "AuthorizationCodeGrant",
        "RefreshTokenGrant",
        "WebhookUseCases",
    }.intersection(calls)


async def test_expired_fill_cannot_restore_old_credentials(
    client: AsyncClient,
    oauth_app: AppDTO,
    user_su_token: TokenResponse,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import asyncio

    from fastid.cache.storage import RedisStorage
    from tests.dependencies import get_test_cache

    started, resume = asyncio.Event(), asyncio.Event()
    original = RedisStorage.set
    first = True

    async def paused_set(self: RedisStorage, key: str, value: Any, **kwargs: Any) -> str:
        nonlocal first
        if key == f"apps:{oauth_app.client_id}" and first:
            first = False
            started.set()
            await resume.wait()
        return await original(self, key, value, **kwargs)

    monkeypatch.setattr(RedisStorage, "set", paused_set)
    task = asyncio.create_task(issue(client, oauth_app))
    try:
        await asyncio.wait_for(started.wait(), timeout=2)
        # Deterministically simulate lease expiry while the first fill is paused.
        await get_test_cache().client.delete(f"lock:apps:{oauth_app.client_id}")
        response = await client.patch(
            f"/apps/{oauth_app.id}",
            json={"client_secret": ROTATED_SECRET},
            headers={"Authorization": f"Bearer {user_su_token.access_token}"},
        )
        assert response.is_success
    finally:
        resume.set()
    assert (await asyncio.wait_for(task, timeout=2)).status_code == status.HTTP_401_UNAUTHORIZED
    assert (await issue(client, oauth_app)).status_code == status.HTTP_401_UNAUTHORIZED


async def test_admin_secret_change_revokes_cached_credentials(
    client: AsyncClient,
    oauth_app: AppDTO,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from starlette.requests import Request

    from fastid.admin.views.settings import AppAdmin
    from tests.dependencies import test_redis, test_session_factory

    monkeypatch.setattr("fastid.cache.dependencies.redis_client", test_redis)
    assert (await issue(client, oauth_app)).status_code == status.HTTP_200_OK
    view = AppAdmin()
    view.session_maker = test_session_factory
    view.is_async = True
    await view.update_model(Request({"type": "http"}), str(oauth_app.id), {"client_secret": ROTATED_SECRET})
    assert (await issue(client, oauth_app)).status_code == status.HTTP_401_UNAUTHORIZED


async def test_cached_token_does_not_checkout_database(client: AsyncClient, oauth_app: AppDTO) -> None:
    from sqlalchemy import event

    from tests.dependencies import test_engine

    assert (await issue(client, oauth_app)).status_code == status.HTTP_200_OK
    checkouts = []

    def record(*args: Any) -> None:
        checkouts.append(True)

    event.listen(test_engine.sync_engine, "checkout", record)
    try:
        response = await issue(client, oauth_app)
    finally:
        event.remove(test_engine.sync_engine, "checkout", record)
    assert response.status_code == status.HTTP_200_OK
    assert not checkouts


async def test_client_validation_reuses_caller_transaction_with_single_connection(oauth_app: AppDTO) -> None:
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from fastid.auth.grants import AuthorizationCodeGrant
    from fastid.database.uow import SQLAlchemyUOW
    from tests.dependencies import get_test_cache, test_engine

    engine = create_async_engine(test_engine.url, pool_size=1, max_overflow=0, pool_timeout=0.2)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with SQLAlchemyUOW(factory) as uow:
            await uow.apps.get(oauth_app.id)
            grant = AuthorizationCodeGrant(uow, get_test_cache(), "http://testserver")
            app = await grant.validate_client(oauth_app.client_id)
            assert app.id == oauth_app.id
            assert uow.session.in_transaction()
    finally:
        await engine.dispose()


async def test_uncommitted_client_state_is_not_published(oauth_app: AppDTO) -> None:
    from fastid.auth.grants import AuthorizationCodeGrant
    from fastid.cache.exceptions import KeyNotFoundError
    from tests.dependencies import get_test_cache, get_test_uow

    cache = get_test_cache()
    async with get_test_uow() as uow:
        app = await uow.apps.get(oauth_app.id)
        app.client_secret = ROTATED_SECRET
        snapshot = await AuthorizationCodeGrant(uow, cache, "http://testserver").validate_client(oauth_app.client_id)
        assert snapshot.client_secret == ROTATED_SECRET
        with pytest.raises(KeyNotFoundError):
            await cache.get(f"apps:{oauth_app.client_id}")
        await uow.rollback()
    grant = AuthorizationCodeGrant(get_test_uow(), cache, "http://testserver")
    assert (await grant.authenticate_client(oauth_app.client_id, oauth_app.client_secret)).id == oauth_app.id
