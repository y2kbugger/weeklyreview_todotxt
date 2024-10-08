from typing import Annotated, Literal

from fastapi import Depends, Form, Request, Response
from fastapi.responses import HTMLResponse

from insync.app.ws_list_updater import WebSocketListUpdater
from insync.db import ListDB
from insync.listitem import ListItem, ListItemProject, ListItemProjectType
from insync.listregistry import ChecklistResetCommand, CompletionCommand, CreateCommand, ListRegistry, RecurringCommand, UndoView
from insync.listview import ListView
from insync.renderer import Renderer

from . import app, get_db, get_registry, get_ws_list_updater, templates


@app.get("/checklist")
def checklist_index(
    request: Request,
    registry: Annotated[ListRegistry, Depends(get_registry)],
) -> HTMLResponse:
    checklist_listview = registry.search(ListItemProject("", ListItemProjectType.checklist))
    checklist_listview = checklist_listview.active
    return templates.TemplateResponse(request, "checklist_index.html", {'checklist_listview': checklist_listview})


@app.post("/checklist/{project_name}/undoredo/{undo_or_redo}")
async def checklist_undo(
    project_name: str,
    undo_or_redo: Literal["undo", "redo"],
    registry: Annotated[ListRegistry, Depends(get_registry)],
    db: Annotated[ListDB, Depends(get_db)],
    ws_list_updater: Annotated[WebSocketListUpdater, Depends(get_ws_list_updater)],
) -> Response:
    project = ListItemProject(project_name, ListItemProjectType.checklist)

    if undo_or_redo == "undo":
        assert registry.undoview().undocommand is not None, "No command to undo"
        registry.undo()
    elif undo_or_redo == "redo":
        assert registry.undoview().redocommand is not None, "No command to redo"
        registry.redo()
    else:
        raise ValueError(f"Invalid undo_or_redo value: {undo_or_redo}")

    db.patch(registry)
    await ws_list_updater.broadcast_update(project)
    return Response(status_code=204)


@app.get("/checklist/{project_name}")
def checklist(project_name: str, request: Request) -> HTMLResponse:
    project = ListItemProject(project_name, ListItemProjectType.checklist)
    return templates.TemplateResponse(request, "checklist.html", {"project": project})


class ChecklistRenderer(Renderer):
    @staticmethod
    def render(listview: ListView, undoview: UndoView) -> str:
        return templates.get_template("checklist_items.html").render(listview=listview.active, undoview=undoview)


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
    item = next(i for i in registry if str(i.uuid) == uuid)
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
    item = next(i for i in registry if str(i.uuid) == uuid)
    cmd = RecurringCommand(item.uuid, recurring)
    registry.do(cmd)
    db.patch(registry)

    await ws_list_updater.broadcast_update(item.project)
    return Response(status_code=204)
