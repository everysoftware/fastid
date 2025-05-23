from typing import Annotated

from fastapi import Depends

from fastid.oauth.use_cases import OAuthUseCases

OAuthAccountsDep = Annotated[OAuthUseCases, Depends()]
