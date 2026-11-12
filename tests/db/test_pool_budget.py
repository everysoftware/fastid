import pytest
from pydantic import ValidationError

from fastid.database.config import DBSettings


@pytest.mark.parametrize(
    ("workers", "budget", "pool", "overflow"), [(1, 100, 100, 40), (16, 100, 100, 40), (4, 17, 2, 40)]
)
def test_pool_never_exceeds_worker_budget(workers: int, budget: int, pool: int, overflow: int) -> None:
    settings = DBSettings(
        _env_file=None,
        url="postgresql+asyncpg://localhost/test",
        workers=workers,
        connection_budget=budget,
        pool_size=pool,
        max_overflow=overflow,
    )
    size, extra = settings.pool_limits
    assert size >= 1
    assert extra >= 0
    assert size <= pool
    assert extra <= overflow
    assert workers * (size + extra) <= budget


def test_budget_rejects_more_workers_than_connections() -> None:
    with pytest.raises(ValidationError, match="budget"):
        DBSettings(_env_file=None, url="postgresql+asyncpg://localhost/test", workers=8, connection_budget=7)


@pytest.mark.parametrize("worker_value", ["", "4"])
def test_worker_budget_follows_gunicorn_environment(worker_value: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTID_GUNICORN_WORKERS", worker_value)
    settings = DBSettings(_env_file=None, url="postgresql+asyncpg://localhost/test")
    assert settings.workers == (1 if worker_value == "" else 4)
