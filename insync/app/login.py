from logging import getLogger
from typing import Annotated

from fastapi import Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from . import app, templates
from .auth_middleware import hash_token

logger = getLogger(__name__)


@app.get("/login")
def get_login(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "login.html", {})


@app.post("/login")
def post_login(token: Annotated[str, Form()]) -> RedirectResponse:
    token_hashed = hash_token(token)
    response = RedirectResponse("/login", status_code=302)

    response.set_cookie(
        key="insyncauthn",
        value=token_hashed,
        max_age=400 * 24 * 60 * 60,  # 400 days
        path="/",
        secure=True,
        httponly=True,
        samesite="lax",  # Safe as long as CORS is not enabled
    )
    return response


@app.get("/logout")
def logout() -> RedirectResponse:
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie(key="insyncauthn")
    return response
