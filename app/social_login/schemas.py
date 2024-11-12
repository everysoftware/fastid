from typing import Self

from app.auth.schemas import User
from app.domain.schemas import DomainModel, BaseModel
from app.domain.types import UUID
from app.oauthlib.schemas import OpenIDBearer


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


class OAuthAccount(DomainModel, OAuthAccountBase):
    user_id: UUID

    @classmethod
    def from_open_id(cls, open_id: OpenIDBearer, user: User) -> Self:
        return cls(
            **open_id.model_dump(exclude={"id", "id_token", "token_type"}),
            account_id=open_id.id,
            user_id=user.id,
        )

    def update(self, open_id: OpenIDBearer) -> Self:
        return self.merge_attrs(
            **open_id.model_dump(exclude={"id", "id_token", "token_type"}),
            account_id=open_id.id,
        )
