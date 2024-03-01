from typing import Annotated

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.websockets import WebSocketState

app = FastAPI()
templates = Jinja2Templates(directory="insync")


class CurrentState(BaseModel):
    message: str


class HtmxMessage(BaseModel):
    message: str
    HEADERS: dict[str, str | None]


_current_global_state = CurrentState(message="<3")


def get_global_state() -> CurrentState:
    return _current_global_state


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, state: CurrentState) -> None:
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
async def hello_ws(websocket: WebSocket, state: Annotated[CurrentState, Depends(get_global_state)]) -> None:
    await manager.connect(websocket, state)
    await manager.broadcast(render_updated_state(state))

    try:
        async for htmx_json in websocket.iter_text():
            print("RX from htmx", htmx_json)
            state.message += '\n' + HtmxMessage.model_validate_json(htmx_json).message
            await manager.broadcast(render_updated_state(state))
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def render_updated_state(state: CurrentState) -> str:
    print(f"TX from python {state.message}")
    html = f"""
    <div id="current-message" hx-swap-oob="true">
        <pre>
        {state.message}
        </pre>
    </div>
    """
    return html


@app.get("/")
def hello(request: Request) -> HTMLResponse:
    print("running hello.html template")
    return templates.TemplateResponse(request, "hello.html", {})
