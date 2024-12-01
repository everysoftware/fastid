import asyncio
import functools
from typing import Annotated, Callable, Coroutine, Any

import typer

from app.auth.schemas import UserCreate
from app.cli.service import CLIManager

app = typer.Typer()


def typer_async[**P, T](
    f: Callable[P, Coroutine[Any, Any, T]],
) -> Callable[P, T]:
    @functools.wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@app.command()
def hc() -> None:
    """Health check. Print hello world"""
    typer.echo("Hello, World!")


@app.command()
@typer_async
async def newuser(
    first_name: Annotated[str, typer.Option(prompt=True)] = "New",
    last_name: Annotated[str, typer.Option(prompt=True)] = "User",
    email: Annotated[str, typer.Option(prompt=True)] = "user@example.com",
    password: Annotated[
        str,
        typer.Option(prompt=True, confirmation_prompt=True, hide_input=True),
    ] = "password",
    is_admin: Annotated[bool, typer.Option(prompt=True)] = False,
) -> None:
    """Register a new user or admin"""
    async with CLIManager() as manager:
        await manager.register_user(
            UserCreate(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            ),
            is_admin,
        )
