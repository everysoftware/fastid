from __future__ import annotations

import datetime
from uuid import UUID

from uuid_utils import uuid7

UUIDv7 = UUID


def uuid_hex() -> str:
    return uuid7().hex


def uuid() -> UUIDv7:
    return UUIDv7(uuid_hex())


def naive_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
