from collections.abc import Iterable
from typing import Annotated

from fastapi import Depends, Form, Request, Response
from fastapi.responses import HTMLResponse

from insync.app.ws_list_updater import WebSocketListUpdater
from insync.db import ListDB
from insync.listregistry import CompletionCommand, CreateCommand, ListItem, ListItemProject, ListItemProjectType, ListRegistry

from . import app, get_db, get_registry, get_ws_list_updater, templates


@app.get("/checklist/{project_name}")
def checklist(project_name: str, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "checklist.html", {"project_name": project_name})


def render_checklist_items(listitems: Iterable[ListItem]) -> str:
    return templates.get_template("checklist_items.html").render(listitems=listitems)

@app.post("/checklist/{project_name}/new")
async def post_checklist(
    project_name: str,
    registry: Annotated[ListRegistry, Depends(get_registry)],
    db: Annotated[ListDB, Depends(get_db)],
    ws_list_updater: Annotated[WebSocketListUpdater, Depends(get_ws_list_updater)],
    description: Annotated[str, Form()],
) -> Response:
    project = ListItemProject(project_name, ListItemProjectType.checklist)
    item = ListItem(description, project=project)

    cmd = CreateCommand(item.uuid, item)
    registry.do(cmd)
    db.patch(registry)

    await ws_list_updater.broadcast_update(item.project)
    return Response(status_code=204)


@app.patch("/checklist/{uuid}/completed")
async def patch_checklist_completed(
    uuid: str,
    registry: Annotated[ListRegistry, Depends(get_registry)],
    db: Annotated[ListDB, Depends(get_db)],
    ws_list_updater: Annotated[WebSocketListUpdater, Depends(get_ws_list_updater)],
    completed: Annotated[bool, Form()] = False,
) -> Response:
    item = next(i for i in registry.items if str(i.uuid) == uuid)
    cmd = CompletionCommand(item.uuid, completed)
    registry.do(cmd)
    db.patch(registry)

    await ws_list_updater.broadcast_update(item.project)
    return Response(status_code=204)
