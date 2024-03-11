from collections import defaultdict
from typing import Callable

from fastapi import WebSocket
from fastapi.websockets import WebSocketState

from insync.listregistry import ListItem, ListItemProject, ListItemProjectType, ListRegistry


class WebsocketListUpdater:
    def __init__(self, registry: ListRegistry):
        self.subscriptions: dict[ListItemProject, list[WebSocket]] = defaultdict(list)
        self.renderer: dict[ListItemProjectType, Callable[[list[ListItem]], str]] = {}
        self.registry = registry

    def register_renderer(self, project_type: ListItemProjectType, renderer: Callable[[list[ListItem]], str]) -> None:
        assert project_type not in self.renderer, f"Renderer for {project_type} already registered"
        self.renderer[project_type] = renderer

    async def subscribe(self, websocket: WebSocket, project: ListItemProject) -> None:
        await websocket.accept()
        self.subscriptions[project].append(websocket)

    def garbage_collect_closed_connections(self) -> None:
        for project, ws_list in self.subscriptions.items():
            self.subscriptions[project] = [ws for ws in ws_list if ws.application_state != WebSocketState.DISCONNECTED]
            self.subscriptions[project] = [ws for ws in ws_list if ws.client_state != WebSocketState.DISCONNECTED]

    async def broadcast_update(self, project: ListItemProject) -> None:
        self.garbage_collect_closed_connections()

        items = [item for item in self.registry.items if project.name in item.project.name]
        html = self.renderer[project.project_type](items)

        for ws in self.subscriptions[project]:
            await self.send_message(ws, html)

    async def send_message(self, ws: WebSocket, message: str) -> None:
        try:
            await ws.send_text(message)
        except RuntimeError:
            print("Failed to send message, this should not happen regularly as connections are garbage collected before broadcasts.")

    def disconnect(self, websocket: WebSocket) -> None:
        for _project, ws_list in self.subscriptions.items():
            if websocket in ws_list:
                ws_list.remove(websocket)
