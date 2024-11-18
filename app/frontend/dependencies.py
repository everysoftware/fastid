from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from app.api.exceptions import Unauthorized
from app.auth.dependencies import AuthDep
from app.auth.schemas import OAuth2ConsentRequest


async def valid_consent(
    auth: AuthDep,
    request: Request,
    consent: Annotated[OAuth2ConsentRequest, Depends()],
) -> OAuth2ConsentRequest:
    if not request.query_params:
        consent_data = request.session.get("consent")
        if consent_data is None:
            raise Unauthorized()
        else:
            consent = OAuth2ConsentRequest.model_validate(consent_data)
    return await auth.validate_consent_request(consent)
