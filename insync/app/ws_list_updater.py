from collections import defaultdict
from typing import Callable

from fastapi import WebSocket
from fastapi.websockets import WebSocketState

from insync.listregistry import ListItem, ListItemProject, ListRegistry


class WebSocketListUpdater:
    def __init__(self, registry: ListRegistry):
        self.registry = registry

        self.subscriptions: dict[ListItemProject, list[WebSocket]] = defaultdict(list)
        self.renderers: dict[ListItemProject, Callable[[list[ListItem]], str]] = {}
        self.filters: dict[ListItemProject, Callable[[ListItem], bool]] = {}

    def register_channel(self, project: ListItemProject, renderer: Callable[[list[ListItem]], str]) -> None:
        if project in self.renderers:
            # This is a no-op if the project is already registered
            return
        self.renderers[project] = renderer
        self.filters[project] = lambda x: x.project in project

    def render_channel(self, channel: ListItemProject) -> str:
        renderer = self.renderers[channel]
        item_filter = self.filters[channel]
        items = [item for item in self.registry.items if item_filter(item)]
        return renderer(items)

    async def subscribe(self, websocket: WebSocket, channel: ListItemProject, renderer: Callable[[list[ListItem]], str]) -> None:
        await websocket.accept()
        self.register_channel(channel, renderer)
        self.subscriptions[channel].append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        for _channel, ws_list in self.subscriptions.items():
            if websocket in ws_list:
                ws_list.remove(websocket)

    def _garbage_collect_closed_connections(self) -> None:
        """Remove all disconnected websockets from the subscriptions."""
        for project, ws_list in self.subscriptions.items():
            self.subscriptions[project] = [ws for ws in ws_list if ws.client_state != WebSocketState.DISCONNECTED]

    async def send_update(self, ws: WebSocket, channel: ListItemProject) -> None:
        """Send an update to a single websocket. This is useful for initial updates."""
        update = self.render_channel(channel)
        await self._send_message(ws, update)

    async def broadcast_update(self, channel: ListItemProject) -> None:
        """Broadcast an update to all websockets subscribed to a given subscription."""
        self._garbage_collect_closed_connections()

        update = self.render_channel(channel)

        for ws in self.subscriptions[channel]:
            await self._send_message(ws, update)

    async def _send_message(self, ws: WebSocket, message: str) -> None:
        try:
            await ws.send_text(message)
        except RuntimeError:
            print("Failed to send message, this should not happen regularly as connections are garbage collected before broadcasts.")

