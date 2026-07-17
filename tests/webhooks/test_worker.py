from fastid.webhooks.config import webhook_settings
from fastid.webhooks.worker import get_retry_delay

FIVE_SECONDS = 5
FIVE_MINUTES = 300
ONE_MINUTE = 60
ONE_DAY = 86400


def test_retry_schedule_without_jitter() -> None:
    assert get_retry_delay(1, None, jitter=1) == FIVE_SECONDS
    assert get_retry_delay(2, None, jitter=1) == FIVE_MINUTES
    assert get_retry_delay(9, None, jitter=1) == ONE_DAY


def test_retry_after_overrides_schedule_and_is_capped() -> None:
    assert get_retry_delay(1, ONE_MINUTE, jitter=1) == ONE_MINUTE
    assert get_retry_delay(1, webhook_settings.retry_after_max_seconds * 2, jitter=1) == ONE_DAY
