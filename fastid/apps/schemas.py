from fastid.core.schemas import BaseModel
from fastid.database.schemas import EntityDTO


class AppBase(BaseModel):
    name: str
    slug: str
    redirect_uris: str
    is_active: bool = True


class AppDTO(EntityDTO, AppBase):
    client_id: str
    client_secret: str


class AppCreate(AppBase):
    client_id: str | None = None
    client_secret: str | None = None


class AppUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    redirect_uris: str | None = None
    is_active: bool | None = None
    client_id: str | None = None
    client_secret: str | None = None
