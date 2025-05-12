import hashlib
import hmac
from typing import Any


def create_telegram_hash(bot_token: str, payload: dict[str, Any]) -> str:
    data_check_string = "\n".join(sorted(f"{k}={v}" for k, v in payload.items()))
    return hmac.new(
        hashlib.sha256(bot_token.encode()).digest(),
        data_check_string.encode(),
        "sha256",
    ).hexdigest()
