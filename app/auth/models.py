from typing import Self

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column, Mapped

from app.auth.exceptions import WrongPassword
from app.auth.schemas import UserCreate
from app.base.models import Entity
from app.base.types import generate_uuid
from app.oauthlib.schemas import OpenIDBearer
from app.utils.hashing import hasher


class User(Entity):
    __tablename__ = "users"

    first_name: Mapped[str]
    last_name: Mapped[str | None]
    email: Mapped[str | None] = mapped_column(index=True)
    new_email: Mapped[str | None] = mapped_column(index=True)
    telegram_id: Mapped[int | None] = mapped_column(index=True)
    hashed_password: Mapped[str | None]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)

    @hybrid_property
    def is_oauth(self) -> bool:
        return bool(self.hashed_password)

    @hybrid_property
    def display_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name:
            return self.first_name
        return ""

    @classmethod
    def from_create(cls, dto: UserCreate) -> Self:
        user = cls(
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email,
        )
        user.set_password(dto.password)
        return user

    @classmethod
    def from_open_id(cls, open_id: OpenIDBearer) -> Self:
        user = cls(
            id=generate_uuid(),
            first_name=open_id.first_name,
            last_name=open_id.last_name,
            email=open_id.email,
        )
        user.verify()
        if open_id.provider == "telegram":
            user.telegram_id = int(open_id.id)
        return user

    def disconnect_open_id(self, provider: str) -> None:
        if provider == "telegram":
            self.telegram_id = None

    def set_password(self, password: str) -> None:
        self.hashed_password = hasher.hash(password)

    def verify_password(self, password: str) -> None:
        if not hasher.verify(password, self.hashed_password):
            raise WrongPassword()

    def grant_superuser(self) -> None:
        self.is_superuser = True

    def revoke_superuser(self) -> None:
        self.is_superuser = False

    def verify(self) -> None:
        self.is_verified = True
