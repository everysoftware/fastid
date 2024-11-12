from enum import StrEnum, auto
from typing import cast, Self

from pydantic import (
    Field,
    EmailStr,
)

from app.domain.schemas import BaseModel, DomainModel
from app.oauthlib.schemas import OpenIDBearer
from app.utils.hashing import hasher


class User(DomainModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    password: str | None = Field(None, exclude=True)
    hashed_password: str | None = None  # Field(None, exclude=True)
    telegram_id: int | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None

    @property
    def is_oauth(self) -> bool:
        return bool(self.hashed_password)

    @property
    def display_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name:
            return self.first_name
        return ""

    def hash_password(self) -> None:
        self.hashed_password = hasher.hash(self.password)

    def verify_password(self, password: str) -> bool:
        return cast(bool, hasher.verify(password, self.hashed_password))

    def change_password(self, password: str) -> None:
        self.password = password
        self.hash_password()

    def grant_superuser(self) -> None:
        self.is_superuser = True

    def revoke_superuser(self) -> None:
        self.is_superuser = False

    def verify(self) -> None:
        self.is_verified = True

    @classmethod
    def from_open_id(cls, open_id: OpenIDBearer) -> Self:
        user = cls(
            first_name=open_id.first_name,
            last_name=open_id.last_name,
            email=open_id.email,
        )
        user.verify()
        if open_id.provider == "telegram":
            user.telegram_id = int(open_id.id)
        return user


class UserCreate(BaseModel):
    first_name: str = Field(examples=["John"])
    last_name: str | None = Field(None, examples=["Doe"])
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None


class TokenType(StrEnum):
    access = auto()
    refresh = auto()
    verify = auto()


class Role(StrEnum):
    user = auto()
    superuser = auto()
