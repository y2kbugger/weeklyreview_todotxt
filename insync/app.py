from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated, Dict, List

from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="insync")

class CurrentState(BaseModel):
    message: str

class HtmxMessage(BaseModel):
    message: str
    HEADERS: Dict[str,str|None]

def make_global_state() -> CurrentState:
    return CurrentState(message="<3")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/hellowebsocket")
async def hello_ws(websocket: WebSocket, state: Annotated[CurrentState, Depends(make_global_state)]):
    await manager.connect(websocket)

    try:
        async for htmx_json in websocket.iter_text():
            print("RX from htmx", htmx_json)
            state.message = HtmxMessage.model_validate_json(htmx_json).message
            await manager.broadcast(render_updated_state(state))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def render_updated_state(state: CurrentState):
    print(f"TX from python {state.message}")
    html = f"""
    <div id="current-message" hx-swap-oob="true">
        {state.message}
    </div>
    """
    return html

@app.get("/")
def hello(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "hello.html", {})
