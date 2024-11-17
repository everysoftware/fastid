from __future__ import annotations

import datetime
from uuid import UUID as PythonUUID

from uuid_utils import uuid7

UUID = PythonUUID


def uuid_hex() -> str:
    return uuid7().hex


def uuid() -> UUID:
    return UUID(uuid_hex())


def naive_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
