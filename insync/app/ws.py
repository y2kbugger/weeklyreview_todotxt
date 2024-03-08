from typing import Annotated

from fastapi import Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from starlette.websockets import WebSocketState

from insync.db import ListDB
from insync.listregistry import ListItem, ListItemProjectType, ListRegistry

from . import app, get_db, get_registry


class HtmxMessage(BaseModel):
    message: str
    HEADERS: dict[str, str | None]


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str) -> None:
        for connection in self.active_connections:
            if connection.client_state == WebSocketState.DISCONNECTED:
                self.disconnect(connection)
            else:
                await connection.send_text(message)


ws_manager = ConnectionManager()
from .checklist import render_checklist  # TODO: fix circular import problem


@app.websocket("/ws/{list_type}")
async def ws(
    list_type: ListItemProjectType,
    websocket: WebSocket,
    registry: Annotated[ListRegistry, Depends(get_registry)],
    db: Annotated[ListDB, Depends(get_db)],
) -> None:
    assert list_type == ListItemProjectType.checklist, f"Only {ListItemProjectType.checklist} is supported currently"
    # TODO: add support for other list types
    # TODO: add support for filtering to a specific "Project" e.g. +^grocery

    await ws_manager.connect(websocket)
    await ws_manager.broadcast(render_checklist(registry.items))

    try:
        async for htmx_json in websocket.iter_text():
            msg = HtmxMessage.model_validate_json(htmx_json).message
            if msg != '':
                registry.add(ListItem(msg))
                db.patch(registry)
            await ws_manager.broadcast(render_checklist(registry.items))
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
