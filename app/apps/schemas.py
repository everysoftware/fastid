from typing import Any, Sequence

from pydantic import field_validator, AnyHttpUrl

from app.base.schemas import EntityDTO, BaseModel


class AppBase(BaseModel):
    name: str
    client_id: str
    client_secret: str
    redirect_uris: Sequence[AnyHttpUrl]
    is_active: bool = True

    @field_validator("redirect_uris", mode="before")
    def validate_redirect_uris(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.split(";")
        return v


class AppDTO(EntityDTO, AppBase):
    pass


class AppCreate(AppBase):
    pass
