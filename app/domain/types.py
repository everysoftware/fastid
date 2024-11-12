from __future__ import annotations

import datetime
from uuid import UUID as PythonUUID

from uuid_utils import uuid7

UUID = PythonUUID


def generate_uuid() -> UUID:
    return UUID(uuid7().hex)


def naive_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
