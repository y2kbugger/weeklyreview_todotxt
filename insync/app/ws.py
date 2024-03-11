from typing import Annotated

from fastapi import Depends, WebSocket, WebSocketDisconnect

from insync.listregistry import ListItemProject, ListItemProjectType, null_listitemproject

from . import app, get_ws_list_updater
from .ws_list_updater import WebsocketListUpdater


async def _ws_keep_alive(ws_list_updater: WebsocketListUpdater, websocket: WebSocket) -> None:
    try:
        async for _htmx_json in websocket.iter_text():
            raise RuntimeError("Message received, but this websocket is mean only to transmit updates.")
    except WebSocketDisconnect:
        ws_list_updater.disconnect(websocket)


@app.websocket("/ws/{list_project_type}/{list_project_name}")
async def ws(
    list_project_type: ListItemProjectType,
    list_project_name: str,
    websocket: WebSocket,
    ws_list_updater: Annotated[WebsocketListUpdater, Depends(get_ws_list_updater)],
) -> None:
    project = ListItemProject(list_project_name, list_project_type)

    await ws_list_updater.subscribe(websocket, project)
    await ws_list_updater.broadcast_update(project)
    await _ws_keep_alive(ws_list_updater, websocket)

