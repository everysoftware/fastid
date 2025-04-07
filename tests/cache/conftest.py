import pytest

from app.cache.adapter import CacheStorage
from tests.mocks import CACHE_RECORD


@pytest.fixture
async def mock_record(cache: CacheStorage) -> dict[str, str]:
    await cache.set(CACHE_RECORD["key"], CACHE_RECORD["value"])
    return CACHE_RECORD
