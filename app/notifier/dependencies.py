from typing import Annotated

from fastapi import Depends

from app.notifier.adapter import INotifier, Notifier

NotifierDep = Annotated[INotifier, Depends(Notifier)]
