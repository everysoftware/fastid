import asyncio
from typing import Callable, Annotated, Any, Coroutine

from fastapi import Depends


class BackgroundTasks:
    @staticmethod
    def add_task[**P](
        func: Callable[P, Coroutine[Any, Any, None]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        asyncio.create_task(func(*args, **kwargs))


BackgroundDep = Annotated[BackgroundTasks, Depends()]
