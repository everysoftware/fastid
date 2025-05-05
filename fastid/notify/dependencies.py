from typing import Annotated

from fastapi import Depends

from fastid.notify.use_cases import NotificationUseCases

NotifyDep = Annotated[NotificationUseCases, Depends()]
