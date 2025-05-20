<p align="center">
    <a href="https://github.com/everysoftware/fastid"><img src="https://raw.githubusercontent.com/everysoftware/fastid/master/assets/logo_text.png" alt="FastID"></a>
</p>
<p align="center">
    <em>FastID authentication platform, high security, lightning fast, easy-to-use, customizable.</em>
</p>

<p align="center">
    <a href="https://github.com/everysoftware/fastid/actions/workflows/test.yml" target="_blank">
        <img src="https://github.com/everysoftware/fastid/actions/workflows/test.yml/badge.svg" alt="Test">
    </a>
    <a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/everysoftware/fastid" target="_blank">
        <img src="https://coverage-badge.samuelcolvin.workers.dev/everysoftware/fastid.svg" alt="Coverage">
    </a>
    <a href="https://github.com/everysoftware/fastid/actions/workflows/codeql.yml" target="_blank">
        <img src="https://github.com/everysoftware/fastid/actions/workflows/codeql.yml/badge.svg" alt="CodeQL">
    </a>
    <a href="https://github.com/everysoftware/fastid/actions/workflows/test.yml" target="_blank">
        <img src="https://img.shields.io/github/actions/workflow/status/everysoftware/fastid/test.yml?label=Bandit+Scan" alt="Bandit">
    </a>
    <a href="https://img.shields.io/github/license/everysoftware/fastid.png" target="_blank">
        <img src="https://img.shields.io/github/license/everysoftware/fastid.png" alt="License">
    </a>
</p>

---

**Live Demo:** [https://fastid.croce.ru](https://fastid.croce.ru)

**Documentation:** [https://everysoftware.github.io/fastid](https://everysoftware.github.io/fastid)

**Source Code:** [https://github.com/everysoftware/fastid](https://github.com/everysoftware/fastid)

---

## Features

* **Secure**: Reliable authentication without exposing user credentials to the clients (thanks
  to [OAuth 2.0](https://oauth.net/) and [OpenID Connect](https://openid.net/)).
* **Fast**: Powered by [FastAPI](https://fastapi.tiangolo.com/) (one of the fastest Python web frameworks
  available)
  and [SQLAlchemy](https://www.sqlalchemy.org/).
* **Easy-to-use**: Comes with an admin dashboard to manage users and applications. Built-in user profile pages for
  account management.
* **Quickly start**: Supports sign up with Google, Yandex, etc. Advanced integration with Telegram.
* **In touch with users**: Greets users after registration and verifies their actions via OTP.
* **Customizable**: Changes the appearance with custom templates for pages and email messages. Functionality can be
  extended with plugins.
* **Observable**: Monitor the platform's performance with 3 pills of observability: logging, metrics and tracing
  complied. Fully compatible with [OpenTelemetry](https://opentelemetry.io/).

## Installation

Clone the repository:

```bash
git clone https://github.com/everysoftware/fastid
```

Generate RSA keys:

```bash
make certs
```

Create a `.env` file based on `.env.example` and run the server:

```bash
make up
```

FastID is available at [http://localhost:8012](http://localhost:8012):

![Sign In](img/signin.png)
![Profile](img/profile.png)
![Connections](img/connections.png)

Admin panel is available at: [http://localhost:8012/admin](http://localhost:8012/admin):

![Admin Login](img/admin_login.png)
![Admin Users](img/admin_users.png)

> To set up observability, you can use [this](https://github.com/everysoftware/fastapi-obs) preset.

Enjoy! 🚀

## Get Started

To start using FastID, you need to [create](http://localhost:8012/admin/app/create) an application in the admin panel.
This will allow you to use FastID for
authentication in your application.

![Sign In](img/create_app.png)

Once you have created an application, you can use the standard OAuth 2.0 flow to authenticate users. FastID supports the
authorization code flow, which is the most secure and recommended way to authenticate users.

Here is an example of how to use FastID for authentication in a Python application using the
[FastAPI](https://fastapi.tiangolo.com/) framework and the [httpx](https://www.python-httpx.org/) library.

```python
from typing import Any, Annotated
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, Response, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

FASTID_URL = "http://localhost:8012"
FASTID_CLIENT_ID = ...
FASTID_CLIENT_SECRET = ...

app = FastAPI()


@app.get("/login")
def login(request: Request) -> Any:
    params = {
        "response_type": "code",
        "client_id": FASTID_CLIENT_ID,
        "redirect_uri": request.url_for("callback"),
    }
    url = f"{FASTID_URL}/authorize?{urlencode(params)}"
    return RedirectResponse(url=url)


@app.get("/callback")
def callback(code: str) -> Any:
    token_data = httpx.post(
        f"{FASTID_URL}/api/v1/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "client_id": FASTID_CLIENT_ID,
            "client_secret": FASTID_CLIENT_SECRET,
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
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No access token")
    response = httpx.get(
        f"{FASTID_URL}/api/v1/userinfo",
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()


@app.get("/test")
def test(user: Annotated[dict[str, Any], Depends(current_user)]) -> Any:
    return user
```

In this example, we define three routes:

1. `/login`: Redirects the user to the FastID authorization page.
2. `/callback`: Handles the callback from FastID after the user has logged in. It exchanges the authorization code for
   an access token and sets it as a cookie.
3. `/test`: A protected route that requires the user to be logged in. It retrieves the user's information from FastID
   using the access token.

Run the FastAPI application:

```bash
fastapi dev examples/httpx.py
```

Visit [http://localhost:8000/login](http://localhost:8000/login) to start the authentication process. After logging in,
you will be redirected to the `/callback` route, where the access token will be set as a cookie. You can then
access the `/test` route to retrieve the user's information.

![Test Response](img/test_response.png)

**Made with ❤️**
