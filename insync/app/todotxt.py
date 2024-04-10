from collections.abc import Iterable
from typing import Literal

from fastapi import Request
from fastapi.responses import HTMLResponse

from insync.listitem import ListItem, ListItemProject, ListItemProjectType

from . import app, templates


@app.get("/todotxt/{project_type}/{project_name}")
def todotxt(
    project_type: Literal['*'] | ListItemProjectType,
    project_name: Literal['*'] | str,
    request: Request,
) -> HTMLResponse:
    if project_type == '*':
        project_type = ListItemProjectType.null
    if project_name == '*':
        project_name = ''
    project = ListItemProject(project_name, project_type)
    return templates.TemplateResponse(request, "todotxt.html", {'project': project})


def render_todotxt_items(project: ListItemProject, listitems: Iterable[ListItem]) -> str:
    return templates.get_template("todotxt_items.html").render(projectj=project, listitems=listitems)
