from typing import Any

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer

from app.main.config import main_settings

oauth2 = OAuth2AuthorizationCodeBearer(
    authorizationUrl=main_settings.authorization_endpoint,
    tokenUrl=main_settings.token_endpoint,
    refreshUrl=main_settings.token_endpoint,
)

app = FastAPI(dependencies=[Depends(oauth2)])


@app.get("/test")
def test() -> Any:
    return {"message": "Hello World"}
