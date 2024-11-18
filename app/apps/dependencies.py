from typing import Annotated

from fastapi import Depends

from app.apps.service import AppUseCases

AppsDep = Annotated[AppUseCases, Depends()]
