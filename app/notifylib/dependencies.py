from typing import Annotated

from fastapi import Depends

from app.notifylib.adapter import INotifier, Notifier

NotifierDep = Annotated[INotifier, Depends(Notifier)]
