from typing import Any

import humanize

from fastid.database.utils import naive_utc

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
    return OPERATION_TYPES[val]
