from pydantic import AnyHttpUrl

from app.apps.schemas import AppDTO


async def validate_client(client_id: str, redirect_uri: AnyHttpUrl) -> AppDTO:
    raise NotImplementedError
