from typing import Any

import humanize

from fastid.database.utils import naive_utc

JSON_SLICE_SIZE = 16
OPERATION_TYPES = {0: "CREATE", 1: "UPDATE", 2: "DELETE"}


def getattr_dot(m: Any, a: Any) -> Any:
    # Handle dot notation for nested attributes
    if "." not in a:
        return getattr(m, a)
    parts = a.split(".")
    obj = m
    for part in parts:
        obj = getattr(obj, part, None)
        if obj is None:
            return None
    return obj


def time_format(m: Any, a: Any) -> Any:
    return humanize.naturaltime(getattr_dot(m, a), when=naive_utc())


def operation_type_format(m: Any, a: Any) -> Any:
    val = getattr(m, a)
    return f"{OPERATION_TYPES[val]} ({val})"


def json_format(m: Any, a: Any) -> Any:
    val = str(getattr(m, a))
    total_length = len(val)
    if total_length <= 2 * JSON_SLICE_SIZE:
        return val
    first_part = val[:JSON_SLICE_SIZE]
    last_part = val[-JSON_SLICE_SIZE:]
    return f"{first_part}...{last_part}"
