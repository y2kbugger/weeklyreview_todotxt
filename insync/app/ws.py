from typing import Annotated

from fastapi import Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from insync.db import ListDB
from insync.listregistry import ListItem, ListItemProject, ListItemProjectType, ListRegistry

from . import app, get_db, get_registry, get_ws_list_updater
from .ws_list_updater import WebsocketListUpdater


class HtmxMessage(BaseModel):
    message: str
    HEADERS: dict[str, str | None]


@app.websocket("/ws/{list_project_type}/{list_project_name}")
async def ws(
    list_project_type: ListItemProjectType,
    list_project_name: str,
    websocket: WebSocket,
    ws_list_updater: Annotated[WebsocketListUpdater, Depends(get_ws_list_updater)],
    registry: Annotated[ListRegistry, Depends(get_registry)],
    db: Annotated[ListDB, Depends(get_db)],
) -> None:
    assert list_project_type == ListItemProjectType.checklist, f"Only {ListItemProjectType.checklist} is supported currently"
    project = ListItemProject(list_project_name, list_project_type)
    # TODO: add support for other list types

    await ws_list_updater.subscribe(websocket, project)
    await ws_list_updater.broadcast_update(project)

    try:
        async for htmx_json in websocket.iter_text():
            msg = HtmxMessage.model_validate_json(htmx_json).message
            if msg != '':
                registry.add(ListItem(msg, project=project))
                db.patch(registry)
            await ws_list_updater.broadcast_update(project)
    except WebSocketDisconnect:
        ws_list_updater.disconnect(websocket)
