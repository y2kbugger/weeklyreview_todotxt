from collections.abc import Iterable

from fastapi import Request
from fastapi.responses import HTMLResponse

from insync.listregistry import ListItem, ListItemProjectType

from . import app, templates


@app.get("/todotxt/{list_project_type}/{list_project_name}")
def todotxt(
    list_project_type: ListItemProjectType,
    list_project_name: str,
    request: Request,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "todotxt.html",
        {
            'list_project_type': list_project_type,
            'list_project_name': list_project_name,
        },
    )


def render_todotxt_items(listitems: Iterable[ListItem]) -> str:
    return templates.get_template("todotxt_items.html").render(listitems=listitems)
