from fastapi import Request
from fastapi.responses import HTMLResponse

from . import app, templates


@app.get("/login", response_class=HTMLResponse)
def get_sqladmin(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "login.html", {})
