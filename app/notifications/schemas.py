from typing import Literal

from app.domain.schemas import BaseModel
from app.domain.types import UUID

NotifyMethod = Literal["telegram", "email"]


class NotifyResponse(BaseModel):
    user_id: UUID
    status: str
    method: NotifyMethod
