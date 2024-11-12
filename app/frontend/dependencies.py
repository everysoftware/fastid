from pydantic import AnyHttpUrl

from app.apps.schemas import App


async def validate_client(client_id: str, redirect_uri: AnyHttpUrl) -> App:
    raise NotImplementedError
