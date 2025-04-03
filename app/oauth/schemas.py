from collections.abc import MutableMapping, Sequence

from pydantic import Field

from app.base.datatypes import UUIDv7
from app.base.schemas import BaseModel, EntityDTO


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
    user_id: UUIDv7


class ProviderMeta(BaseModel):
    name: str
    title: str
    icon: str
    color: str
    authorization_url: str
    revoke_url: str
    enabled: bool = True


class RegistryMeta(BaseModel):
    providers: MutableMapping[str, ProviderMeta] = Field(default_factory=dict)

    @property
    def enabled_providers(self) -> Sequence[ProviderMeta]:
        return list(self.providers.values())

    @property
    def any_enabled(self) -> bool:
        return any(meta.enabled for meta in self.providers.values())
