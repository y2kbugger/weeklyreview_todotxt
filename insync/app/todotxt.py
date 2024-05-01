from typing import Literal

from fastapi import Request
from fastapi.responses import HTMLResponse

from insync.listitem import ListItemProject, ListItemProjectType
from insync.listregistry import UndoView
from insync.listview import ListView
from insync.renderer import Renderer

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


class TodoTxtRenderer(Renderer):
    @staticmethod
    def render(listview: ListView, undoview: UndoView) -> str:
        project = listview.project
        listitems = listview.active
        return templates.get_template("todotxt_items.html").render(projectj=project, listitems=listitems)
