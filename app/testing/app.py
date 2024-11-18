from typing import Any

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer

from app.auth.config import auth_settings

oauth2 = OAuth2AuthorizationCodeBearer(
    authorizationUrl=auth_settings.authorization_endpoint,
    tokenUrl=auth_settings.token_endpoint,
    refreshUrl=auth_settings.token_endpoint,
)

app = FastAPI(dependencies=[Depends(oauth2)])


@app.get("/test")
def test() -> Any:
    return {"message": "Hello World"}
