import pytest

from fastid.database.schemas import LimitOffset, Sorting
from fastid.database.uow import SQLAlchemyUOW


@pytest.fixture(autouse=True)
async def _enable_oauth_providers(_start_app: None, uow: SQLAlchemyUOW) -> None:
    providers = await uow.oauth_providers.get_many(
        pagination=LimitOffset(limit=10),
        sorting=Sorting(),
    )
    for provider in providers.items:
        provider.enabled = True
        provider.client_id = f"{provider.name}-client-id"
        provider.client_secret = (
            "123456789:test-telegram-client-secret" if provider.name == "telegram" else f"{provider.name}-client-secret"
        )
    await uow.commit()
