from enum import StrEnum, auto

from app.base.schemas import EntityDTO, BaseModel
from app.base.types import UUID


class OAuthAccountBase(BaseModel):
    provider: str

    # Identity
    account_id: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    picture: str | None = None

    # Access
    access_token: str | None = None
    refresh_token: str | None = None
    expires_in: int | None = None
    scope: str | None = None


class OAuthAccountDTO(EntityDTO, OAuthAccountBase):
    user_id: UUID


class OAuthName(StrEnum):
    google = auto()
    yandex = auto()
    telegram = auto()
