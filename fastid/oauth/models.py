from __future__ import annotations

from typing import TYPE_CHECKING, Self
from uuid import UUID  # noqa: TCH003

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastid.database.base import Entity

if TYPE_CHECKING:
    from fastid.auth.models import User
    from fastid.database.utils import UUIDv7
    from fastid.oauth.schemas import OpenIDBearer


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
    def from_open_id(cls, open_id: OpenIDBearer, user_id: UUIDv7) -> Self:
        return cls(
            **open_id.model_dump(exclude={"id", "id_token", "token_type", "token_id"}),
            account_id=open_id.id,
            user_id=user_id,
        )
