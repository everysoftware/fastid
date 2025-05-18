# Get Started

Congratulations! You have successfully installed FastID. Now you can start using it.

Login to admin panel: [http://localhost:8012/admin](http://localhost:8012/admin) and create new app to obtain
`client_id` and `client_secret`.

![Sign In](assets/create_app.png)

Here is an example of client app that uses FastID for authentication:

```python
from typing import Any, Annotated
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, Response, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse

from test_client.config import settings

app = FastAPI()


@app.get("/login")
def login(request: Request) -> Any:
    params = {
        "response_type": "code",
        "client_id": settings.client_id,
        "redirect_uri": request.url_for("callback"),
    }
    url = f"{settings.fastid_url}/authorize?{urlencode(params)}"
    return RedirectResponse(url=url)


@app.get("/callback")
def callback(code: str) -> Any:
    token_data = httpx.post(
        f"{settings.fastid_url}/api/v1/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "client_id": settings.client_id,
            "client_secret": settings.client_secret,
            "code": code,
        },
    )
    token = token_data.json()
    response = Response(content="You are now logged in!")
    response.set_cookie("access_token", token["access_token"])
    return response


def current_user(request: Request) -> dict[str, Any]:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "No access token")
    response = httpx.get(
        f"{settings.fastid_url}/api/v1/userinfo",
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()


@app.get("/test")
def test(user: Annotated[dict[str, Any], Depends(current_user)]) -> Any:
    return user
```

Run the server:

```bash
fastapi dev test_client/fastid.py
```

Go to [http://localhost:8000/login](http://localhost:8000/login) to login in FastID. You will be redirected to
FastID to enter your credentials. After successful login you will be redirected back to the client app
and receive an access token.

Now you can access the protected route [http://localhost:8000/test](http://localhost:8000/test):

![Sign In](assets/test_response.png)

See the full example in the `test_client` directory.
