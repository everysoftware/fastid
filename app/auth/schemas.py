from enum import StrEnum, auto

from pydantic import (
    Field,
    EmailStr,
)

from app.base.schemas import BaseModel, EntityDTO


class UserDTO(EntityDTO):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    hashed_password: str | None = Field(None, exclude=True)
    telegram_id: int | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None


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
