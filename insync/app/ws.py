from typing import Annotated, Literal

from fastapi import Depends, WebSocket, WebSocketDisconnect
from fastapi.params import Query

from insync.app.checklist import render_checklist_items
from insync.app.todotxt import render_todotxt_items
from insync.listitem import ListItemProject, ListItemProjectType

from . import app, get_ws_list_updater
from .ws_list_updater import WebSocketListUpdater


async def _ws_keep_alive(ws_list_updater: WebSocketListUpdater, websocket: WebSocket) -> None:
    try:
        async for _htmx_json in websocket.iter_text():
            raise RuntimeError("Message received, but this websocket is mean only to transmit updates.")
    except WebSocketDisconnect:
        ws_list_updater.disconnect(websocket)


renderers = {
    "checklist": render_checklist_items,
    "todotxt": render_todotxt_items,
}


@app.websocket("/ws/{project_type}/{project_name}")
async def ws(
    project_type: Literal['*'] | ListItemProjectType,
    project_name: Literal['*'] | str,
    renderer_name: Annotated[str, Query()],
    websocket: WebSocket,
    ws_list_updater: Annotated[WebSocketListUpdater, Depends(get_ws_list_updater)],
) -> None:
    if project_type == "*":
        project_type = ListItemProjectType.null
    if project_name == "*":
        project_name = ""
    project = ListItemProject(project_name, project_type)

    try:
        renderer = renderers[renderer_name]
    except KeyError as e:
        raise NotImplementedError(f"Renderer for {renderer_name} not implemented") from e

    channel = await ws_list_updater.subscribe(websocket, project, renderer)
    await ws_list_updater.send_update(websocket, channel)
    await _ws_keep_alive(ws_list_updater, websocket)
