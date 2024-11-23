from typing import Annotated

from fastapi import Depends

from app.notify.service import NotificationUseCases

NotifyDep = Annotated[NotificationUseCases, Depends()]
