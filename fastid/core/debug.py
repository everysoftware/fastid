from fastapi import APIRouter

from fastid.api.exceptions import TestError

debug_router = APIRouter(
    prefix="/debug",
    include_in_schema=False,
)


@debug_router.get("/exc")
def exc() -> None:
    raise TestError
