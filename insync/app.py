import os
from collections.abc import Iterable
from contextlib import asynccontextmanager
from typing import Annotated

import jinja2
from fastapi import Depends, FastAPI, Form, WebSocket, WebSocketDisconnect
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.websockets import WebSocketState

from insync.db import ListDB
from insync.list import CompletionCommand, ListItem, ListRegistry


def persist_to_db():
    app.state.db.patch(app.state.registry)


@asynccontextmanager
async def lifespan(app: FastAPI):
    DB_STR = os.environ.get('INSYNC_DB_STR', ':memory:')
    app.state.db = ListDB(DB_STR)
    app.state.db.ensure_tables_created()
    app.state.registry = app.state.db.load()

    yield

    persist_to_db()
    app.state.db.close()


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="insync")


class HtmxMessage(BaseModel):
    message: str
    HEADERS: dict[str, str | None]

def get_registry() -> ListRegistry:
    return app.state.registry


def get_db() -> ListDB:
    return app.state.db


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


manager = ConnectionManager()


@app.websocket("/hellowebsocket")
async def hello_ws(
    websocket: WebSocket,
    registry: Annotated[ListRegistry, Depends(get_registry)],
    db: Annotated[ListDB, Depends(get_db)],
) -> None:
    await manager.connect(websocket)
    await manager.broadcast(render_updated_state(registry.items))

    try:
        async for htmx_json in websocket.iter_text():
            msg = HtmxMessage.model_validate_json(htmx_json).message
            if msg != '':
                registry.add(ListItem(msg))
                db.patch(registry)
            await manager.broadcast(render_updated_state(registry.items))
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def render_updated_state(listitems: Iterable[ListItem]) -> str:
    template: jinja2.Template = templates.get_template("list.html")
    return template.render(listitems=listitems)


@app.get("/")
def hello(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "hello.html", {})

@app.patch("/list/{uuid}/completed")
async def patch_list(
    uuid: str,
    registry: Annotated[ListRegistry, Depends(get_registry)],
    db: Annotated[ListDB, Depends(get_db)],
    completed: Annotated[bool, Form()] = False,
) -> None:
    print(f'patch_list({uuid=}, {completed=})')

    item = next(i for i in registry.items if str(i.uuid) == uuid)
    cmd = CompletionCommand(item.uuid, completed)
    registry.do(cmd)
    db.patch(registry)
    await manager.broadcast(render_updated_state(registry.items))
