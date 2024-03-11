from collections.abc import Iterable
from typing import Annotated

from fastapi import Depends, Form, Request, Response
from fastapi.responses import HTMLResponse

from insync.app.ws import WebsocketListUpdater, get_ws_list_updater
from insync.db import ListDB
from insync.listregistry import CompletionCommand, ListItem, ListRegistry

from . import app, get_db, get_registry, templates


@app.get("/checklist/{project_name}")
def checklist(project_name: str, request: Request) -> HTMLResponse:
    print(f'checklist/({project_name=})')
    return templates.TemplateResponse(request, "checklist.html", {"project_name": project_name})


def render_checklist(listitems: Iterable[ListItem]) -> str:
    return templates.get_template("checklist_items.html").render(listitems=listitems)


@app.patch("/checklist/{uuid}/completed")
async def patch_checklist_completed(
    uuid: str,
    registry: Annotated[ListRegistry, Depends(get_registry)],
    db: Annotated[ListDB, Depends(get_db)],
    ws_list_updater: Annotated[WebsocketListUpdater, Depends(get_ws_list_updater)],
    completed: Annotated[bool, Form()] = False,
) -> Response:
    print(f'patch_list({uuid=}, {completed=})')

    item = next(i for i in registry.items if str(i.uuid) == uuid)
    cmd = CompletionCommand(item.uuid, completed)
    registry.do(cmd)
    db.patch(registry)

    await ws_list_updater.broadcast_update(item.project)
    return Response(status_code=204)
