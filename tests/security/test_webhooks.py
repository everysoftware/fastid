import pytest

from fastid.security.webhooks import generate_headers, verify_headers
from tests.mocks import WEBHOOK_PAYLOAD, WEBHOOK_TEST_DATA


@pytest.mark.parametrize(
    ("timestamp", "webhook_id", "generate_secret_key", "verify_secret_key", "expected"), WEBHOOK_TEST_DATA
)
def test_verify_headers(
    timestamp: int, webhook_id: str, generate_secret_key: str, verify_secret_key: str, *, expected: bool
) -> None:
    headers = generate_headers(WEBHOOK_PAYLOAD, timestamp, webhook_id, generate_secret_key)
    assert verify_headers(WEBHOOK_PAYLOAD, headers, verify_secret_key) == expected
