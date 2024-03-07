from fastapi import Request
from fastapi.responses import HTMLResponse

from . import app, templates


@app.get("/")
def hello(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", {})
