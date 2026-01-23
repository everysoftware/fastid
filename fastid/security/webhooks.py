from fastid.database.utils import uuid


def get_event_id() -> str:
    return str(uuid())
