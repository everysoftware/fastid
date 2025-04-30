import pytest

from fastid.cache.exceptions import KeyNotFoundError
from fastid.cache.storage import CacheStorage


async def test_keys(cache: CacheStorage, mock_record: dict[str, str]) -> None:
    keys = await cache.keys()
    assert len(keys) == 1
    assert mock_record["key"] in keys


async def test_get(cache: CacheStorage, mock_record: dict[str, str]) -> None:
    value = await cache.get(mock_record["key"])
    assert value == mock_record["value"]


async def test_get_non_existent(cache: CacheStorage) -> None:
    with pytest.raises(KeyNotFoundError):
        await cache.get("test")


async def test_update(cache: CacheStorage, mock_record: dict[str, str]) -> None:
    await cache.set(mock_record["key"], "new_value")
    value = await cache.get(mock_record["key"])
    assert value == "new_value"


async def test_delete(cache: CacheStorage, mock_record: dict[str, str]) -> None:
    await cache.delete(mock_record["key"])
    keys = await cache.keys()
    assert mock_record["key"] not in keys


async def test_pop(cache: CacheStorage, mock_record: dict[str, str]) -> None:
    value = await cache.pop(mock_record["key"])
    assert value == mock_record["value"]
    keys = await cache.keys()
    assert mock_record["key"] not in keys


async def test_pop_non_existent(cache: CacheStorage) -> None:
    with pytest.raises(KeyNotFoundError):
        await cache.pop("test")
