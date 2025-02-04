from __future__ import annotations

from typing import Self, TYPE_CHECKING
from uuid import UUID

from auth365.schemas import OpenIDBearer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import Entity

if TYPE_CHECKING:
    from app.auth.models import User


class OAuthAccount(Entity):
    __tablename__ = "oauth_accounts"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    provider: Mapped[str]
    account_id: Mapped[str]
    access_token: Mapped[str | None]
    expires_in: Mapped[int | None]
    scope: Mapped[str | None]
    id_token: Mapped[str | None]
    refresh_token: Mapped[str | None]

    # Personal data
    email: Mapped[str | None] = mapped_column(index=True)
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    display_name: Mapped[str | None]
    picture: Mapped[str | None]

    user: Mapped[User] = relationship(back_populates="oauth_accounts")

    @classmethod
    def from_open_id(cls, open_id: OpenIDBearer, user: User) -> Self:
        return cls(
            **open_id.model_dump(exclude={"id", "id_token", "token_type", "token_id"}),
            account_id=open_id.id,
            user_id=user.id,
        )

    def update(self, open_id: OpenIDBearer) -> Self:
        return self.merge_attrs(
            **open_id.model_dump(exclude={"id", "id_token", "token_type", "token_id"}),
            account_id=open_id.id,
        )
