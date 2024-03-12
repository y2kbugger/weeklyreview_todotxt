from collections.abc import Iterable

from fastapi import Request
from fastapi.responses import HTMLResponse

from insync.listregistry import ListItem

from . import app, templates


@app.get("/todotxt")
def todotxt(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "todotxt.html", {})


def render_todotxt_items(listitems: Iterable[ListItem]) -> str:
    return templates.get_template("todotxt_items.html").render(listitems=listitems)
