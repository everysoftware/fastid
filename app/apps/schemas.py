from collections.abc import Sequence
from typing import Any

from pydantic import AnyHttpUrl, field_validator

from app.base.schemas import BaseModel, EntityDTO


class AppBase(BaseModel):
    name: str
    slug: str
    client_id: str
    client_secret: str
    redirect_uris: Sequence[AnyHttpUrl]
    is_active: bool = True

    @field_validator("redirect_uris", mode="before")
    def validate_redirect_uris(self, v: Any) -> Any:
        if isinstance(v, str):
            return v.split(";")
        return v


class AppDTO(EntityDTO, AppBase):
    pass


class AppCreate(AppBase):
    pass
