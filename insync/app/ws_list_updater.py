from collections import defaultdict
from typing import Callable, TypeAlias

from fastapi import WebSocket
from fastapi.websockets import WebSocketState

from insync.listregistry import ListItem, ListItemProject, ListRegistry

Renderer: TypeAlias = Callable[[ListItemProject, list[ListItem]], str]


class ProjectChannel:
    def __init__(self, project: ListItemProject, renderer: Renderer):
        self.project = project
        self.renderer = renderer

    def __hash__(self) -> int:
        return hash((self.project, self.renderer))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProjectChannel):
            return False
        return self.project == other.project and self.renderer == other.renderer

    def item_filter(self, item: ListItem) -> bool:
        return item.project in self.project

    def broadcast_filter(self, broadcast: ListItemProject) -> bool:
        return broadcast in self.project


class WebSocketListUpdater:
    def __init__(self, registry: ListRegistry):
        self.registry = registry

        self.subscriptions: dict[ProjectChannel, list[WebSocket]] = defaultdict(list)
        self._channels: set[ProjectChannel] = set()

    def register_projectchannel(self, project: ListItemProject, renderer: Renderer) -> ProjectChannel:
        """No-op if already registered, handled by the nature of sets."""
        channel = ProjectChannel(project, renderer)
        self._channels.add(channel)
        return channel

    def render_channel(self, channel: ProjectChannel) -> str:
        items = [item for item in self.registry.items if channel.item_filter(item)]
        return channel.renderer(channel.project, items)

    async def subscribe(self, websocket: WebSocket, project: ListItemProject, renderer: Renderer) -> ProjectChannel:
        await websocket.accept()
        channel = self.register_projectchannel(project, renderer)
        self.subscriptions[channel].append(websocket)
        return channel

    def disconnect(self, websocket: WebSocket) -> None:
        for _channel, ws_list in self.subscriptions.items():
            if websocket in ws_list:
                ws_list.remove(websocket)

    def _garbage_collect_closed_connections(self) -> None:
        """Remove all disconnected websockets from the subscriptions."""
        for project, ws_list in self.subscriptions.items():
            self.subscriptions[project] = [ws for ws in ws_list if ws.client_state != WebSocketState.DISCONNECTED]

    async def send_update(self, ws: WebSocket, channel: ProjectChannel) -> None:
        """Send an update to a single websocket. This is useful for initial updates."""
        update = self.render_channel(channel)
        await self._send_message(ws, update)

    async def broadcast_update(self, project: ListItemProject) -> None:
        """Broadcast an update to all websockets subscribed to a given subscription."""
        self._garbage_collect_closed_connections()

        for channel in self._channels:
            if not channel.broadcast_filter(project):
                continue

            update = self.render_channel(channel)

            for ws in self.subscriptions[channel]:
                await self._send_message(ws, update)

    async def _send_message(self, ws: WebSocket, message: str) -> None:
        try:
            await ws.send_text(message)
        except RuntimeError:
            print("Failed to send message, this should not happen regularly as connections are garbage collected before broadcasts.")
