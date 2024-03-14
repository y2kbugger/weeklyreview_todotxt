from typing import Annotated

from fastapi import Depends, WebSocket, WebSocketDisconnect

from insync.app.checklist import render_checklist_items
from insync.app.todotxt import render_todotxt_items
from insync.listregistry import ListItemProject, ListItemProjectType, NullListItemProject

from . import app, get_ws_list_updater
from .ws_list_updater import WebSocketListUpdater


async def _ws_keep_alive(ws_list_updater: WebSocketListUpdater, websocket: WebSocket) -> None:
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
    ws_list_updater: Annotated[WebSocketListUpdater, Depends(get_ws_list_updater)],
) -> None:
    project = ListItemProject(list_project_name, list_project_type)

    print(f"wsproj: {project}")
    print(f"existing renderers: {ws_list_updater.renderers}")
    if project not in ws_list_updater.renderers:
        print(f"registering {project}")
        if list_project_type == ListItemProjectType.checklist:
            renderer = render_checklist_items
        else:
            raise NotImplementedError(f"Renderer for {list_project_type} not implemented")

        ws_list_updater.register_project_channel(project, renderer)

    await ws_list_updater.subscribe_to_channel(websocket, project)
    await ws_list_updater.send_update(websocket, project)
    await _ws_keep_alive(ws_list_updater, websocket)


@app.websocket("/ws/all")
async def ws_all(
    websocket: WebSocket,
    ws_list_updater: Annotated[WebSocketListUpdater, Depends(get_ws_list_updater)],
) -> None:
    project = NullListItemProject()

    if project not in ws_list_updater.renderers:
        ws_list_updater.register_project_channel(project, render_todotxt_items)

    await ws_list_updater.subscribe_to_channel(websocket, project)
    await ws_list_updater.send_update(websocket, project)
    await _ws_keep_alive(ws_list_updater, websocket)
