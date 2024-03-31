from collections.abc import Iterable
from typing import Annotated

from fastapi import Depends, Form, Request, Response
from fastapi.responses import HTMLResponse

from insync.app.ws_list_updater import WebSocketListUpdater
from insync.db import ListDB
from insync.listregistry import ChecklistResetCommand, CompletionCommand, CreateCommand, ListItem, ListItemProject, ListItemProjectType, ListRegistry, RecurringCommand

from . import app, get_db, get_registry, get_ws_list_updater, templates


@app.get("/checklist/{project_name}")
def checklist(project_name: str, request: Request) -> HTMLResponse:
    project = ListItemProject(project_name, ListItemProjectType.checklist)
    return templates.TemplateResponse(request, "checklist.html", {"project": project})


def render_checklist_items(project: ListItemProject, listitems: Iterable[ListItem]) -> str:
    return templates.get_template("checklist_items.html").render(project=project, listitems=listitems)


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

@app.post("/checklist/{project_name}/reset")
async def post_checklist_reset(
    project_name: str,
    registry: Annotated[ListRegistry, Depends(get_registry)],
    db: Annotated[ListDB, Depends(get_db)],
    ws_list_updater: Annotated[WebSocketListUpdater, Depends(get_ws_list_updater)],
) -> Response:
    project = ListItemProject(project_name, ListItemProjectType.checklist)

    cmd = ChecklistResetCommand(project)
    registry.do(cmd)
    db.patch(registry)

    await ws_list_updater.broadcast_update(project)
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

@app.patch("/checklist/{uuid}/recurring")
async def patch_checklist_recurring(
    uuid: str,
    registry: Annotated[ListRegistry, Depends(get_registry)],
    db: Annotated[ListDB, Depends(get_db)],
    ws_list_updater: Annotated[WebSocketListUpdater, Depends(get_ws_list_updater)],
    recurring: Annotated[bool, Form()],
) -> Response:
    print(f"uuid: {uuid}, recurring: {recurring}")
    item = next(i for i in registry.items if str(i.uuid) == uuid)
    cmd = RecurringCommand(item.uuid, recurring)
    registry.do(cmd)
    db.patch(registry)

    await ws_list_updater.broadcast_update(item.project)
    return Response(status_code=204)
