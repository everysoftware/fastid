# from typing import Annotated, Any
#
# from fastapi import Depends, FastAPI
# from fastapi.responses import RedirectResponse
# from fastlink import CustomOAuth
# from fastlink.schemas import OAuth2Callback
# from starlette.responses import JSONResponse
#
# app = FastAPI()
# fastid = CustomOAuth(settings.client_id, settings.client_secret, settings.redirect_uri, server_url="http://localhost:8012")
#
#
# @app.get("/login")
# async def login() -> Any:
#     url = await fastid.get_authorization_url()
#     return RedirectResponse(url=url)
#
#
# @app.get("/callback")
# async def oauth_callback(callback: Annotated[OAuth2Callback, Depends()]) -> Any:
#     user = await fastid.authorize(callback)
#     return JSONResponse(content=user.model_dump())
