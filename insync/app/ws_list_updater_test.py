from typing import Any
from unittest.mock import Mock

import pytest
from fastapi.websockets import WebSocketState

from insync.app.ws_list_updater import WebSocketListUpdater
from insync.listregistry import ListItem, ListItemProject, ListItemProjectType, ListRegistry, NullListItemProject


@pytest.fixture
def reg() -> ListRegistry:
    return ListRegistry()


@pytest.fixture
def updater(reg: ListRegistry) -> WebSocketListUpdater:
    return WebSocketListUpdater(reg)


class MockRenderer:
    def __init__(self):
        self.calls = []

    def __call__(self, project: ListItemProject, items: list[ListItem]):
        self.calls.append(items)
        return str(project) + ':' + ','.join([item.description for item in items])


@pytest.fixture
def renderer() -> MockRenderer:
    return MockRenderer()


class TestRendering:
    def test_can_render_channel_subscription(
        self,
        reg: ListRegistry,
        updater: WebSocketListUpdater,
        renderer: MockRenderer,
    ) -> None:
        item = ListItem('test1A')
        reg.add(item)
        channel = updater.register_projectchannel(item.project, renderer)

        result = updater.render_channel(channel)

        assert len(renderer.calls) == 1
        assert result == ':test1A'

    def test_when_rendered_only_matched_item_included(
        self,
        reg: ListRegistry,
        updater: WebSocketListUpdater,
        renderer: MockRenderer,
    ) -> None:
        reg.add(ListItem('test'))
        reg.add(ListItem('testT', project=ListItemProject('travel', ListItemProjectType.checklist)))
        reg.add(ListItem('testG', project=ListItemProject('grocery', ListItemProjectType.checklist)))
        project = ListItemProject('grocery', ListItemProjectType.checklist)
        channel = updater.register_projectchannel(project, renderer)

        result = updater.render_channel(channel)

        assert len(renderer.calls) == 1
        assert result == '+^grocery:testG'

    def test_can_project_channel_gets_all_with_matching_root_project(
        self,
        reg: ListRegistry,
        updater: WebSocketListUpdater,
        renderer: MockRenderer,
    ) -> None:
        reg.add(ListItem('test1A'))
        reg.add(ListItem('test2C', project=ListItemProject('travel', ListItemProjectType.checklist)))
        reg.add(ListItem('test2A', project=ListItemProject('grocery', ListItemProjectType.checklist)))
        reg.add(ListItem('test3A', project=ListItemProject('grocery.produce', ListItemProjectType.checklist)))
        reg.add(ListItem('test4B', project=ListItemProject('grocery.camping', ListItemProjectType.todo)))

        project = ListItemProject('grocery', ListItemProjectType.checklist)
        channel = updater.register_projectchannel(project, renderer)

        result = updater.render_channel(channel)

        # 2c is excluded because it's a different checklist
        # 4b is excluded because it's not a checklist
        assert result == '+^grocery:test2A,test3A'

    def test_projects_can_be_a_subset(
        self,
        reg: ListRegistry,
        updater: WebSocketListUpdater,
        renderer: MockRenderer,
    ) -> None:
        """This was a bug caused by using the raw str contains as the filter method for projects."""
        reg.add(ListItem('t1', project=ListItemProject('grocery', ListItemProjectType.checklist)))
        reg.add(ListItem('t2', project=ListItemProject('grocery.produce', ListItemProjectType.checklist)))
        reg.add(ListItem('t3', project=ListItemProject('gro', ListItemProjectType.checklist)))
        reg.add(ListItem('xx', project=ListItemProject('gro', ListItemProjectType.todo)))

        project_grocery = ListItemProject('grocery', ListItemProjectType.checklist)
        channel_grocery = updater.register_projectchannel(project_grocery, renderer)

        project_gro = ListItemProject('gro', ListItemProjectType.checklist)
        channel_gro = updater.register_projectchannel(project_gro, renderer)

        # Act
        result_grocery = updater.render_channel(channel_grocery)
        result_gro = updater.render_channel(channel_gro)

        # Assert
        assert result_grocery == '+^grocery:t1,t2'
        assert result_gro == '+^gro:t3'


class TestBroadcasting:
    class MockWebSocket(Mock):
        client_state = WebSocketState.CONNECTED

        def __init__(self):
            super().__init__()
            self.sent = None
            self.accepted = False

        async def accept(self) -> None:
            self.accepted = True

        async def send_text(self, message: str) -> None:
            assert self.accepted, "Cannot send text before accepting the connection"
            assert self.sent is None, "Mock can only can handle a single sent message"
            self.sent = message

        def spy_sent_text(self) -> str:
            assert self.accepted, "Cannot spy on sent text before accepting the connection"
            assert self.sent is not None, "No text has been sent"
            return self.sent

    @pytest.fixture
    def ws(self, anyio_backend: tuple[str, dict[str, Any]]) -> MockWebSocket:
        return self.MockWebSocket()

    @pytest.fixture
    def ws2(self, anyio_backend: tuple[str, dict[str, Any]]) -> MockWebSocket:
        return self.MockWebSocket()

    async def test_broadcast_to_channel(
        self,
        reg: ListRegistry,
        updater: WebSocketListUpdater,
        renderer: MockRenderer,
        ws: MockWebSocket,
    ) -> None:
        reg.add(ListItem('test1A'))
        await updater.subscribe(ws, NullListItemProject(), renderer)

        await updater.broadcast_update(NullListItemProject())
        result = ws.spy_sent_text()

        assert len(renderer.calls) == 1
        assert result == ':test1A'

    async def test_broadcast_to_channel_updates_only_same_channel(
        self,
        reg: ListRegistry,
        updater: WebSocketListUpdater,
        renderer: MockRenderer,
        ws: MockWebSocket,
    ) -> None:
        reg.add(ListItem('test'))
        reg.add(ListItem('testT', project=ListItemProject('travel', ListItemProjectType.checklist)))
        reg.add(ListItem('testG', project=ListItemProject('grocery', ListItemProjectType.checklist)))
        project = ListItemProject('grocery', ListItemProjectType.checklist)
        await updater.subscribe(ws, project, renderer)

        await updater.broadcast_update(project)
        result = ws.spy_sent_text()

        assert len(renderer.calls) == 1
        assert result == '+^grocery:testG'

    async def test_broadcast_to_channel_updates_parent_subscription(
        self,
        reg: ListRegistry,
        updater: WebSocketListUpdater,
        renderer: MockRenderer,
        ws: MockWebSocket,
    ) -> None:
        reg.add(ListItem('testG', project=ListItemProject('grocery', ListItemProjectType.checklist)))
        reg.add(ListItem('testGP', project=ListItemProject('grocery.produce', ListItemProjectType.checklist)))
        await updater.subscribe(ws, ListItemProject('grocery', ListItemProjectType.checklist), renderer)

        await updater.broadcast_update(ListItemProject('grocery.produce', ListItemProjectType.checklist))
        result = ws.spy_sent_text()

        assert len(renderer.calls) == 1
        assert result == '+^grocery:testG,testGP'

    async def test_broadcast_to_parent_channel_spares_child_subscription(
        self,
        reg: ListRegistry,
        updater: WebSocketListUpdater,
        renderer: MockRenderer,
        ws: MockWebSocket,
    ) -> None:
        reg.add(ListItem('testG', project=ListItemProject('grocery', ListItemProjectType.checklist)))
        reg.add(ListItem('testGP', project=ListItemProject('grocery.produce', ListItemProjectType.checklist)))
        await updater.subscribe(ws, ListItemProject('grocery.produce', ListItemProjectType.checklist), renderer)

        await updater.broadcast_update(ListItemProject('grocery', ListItemProjectType.checklist))
        with pytest.raises(AssertionError):
            ws.spy_sent_text()

        assert len(renderer.calls) == 0

    async def test_broadcast_to_child_channel_renders_only_child(
        self,
        reg: ListRegistry,
        updater: WebSocketListUpdater,
        renderer: MockRenderer,
        ws: MockWebSocket,
    ) -> None:
        reg.add(ListItem('testG', project=ListItemProject('grocery', ListItemProjectType.checklist)))
        reg.add(ListItem('testGP', project=ListItemProject('grocery.produce', ListItemProjectType.checklist)))
        await updater.subscribe(ws, ListItemProject('grocery.produce', ListItemProjectType.checklist), renderer)

        await updater.broadcast_update(ListItemProject('grocery.produce', ListItemProjectType.checklist))
        result = ws.spy_sent_text()

        assert len(renderer.calls) == 1
        assert result == '+^grocery.produce:testGP'

    async def test_renderer_is_called_only_once_per_broadcast_with_two_identical_subscribers(
        self,
        reg: ListRegistry,
        updater: WebSocketListUpdater,
        renderer: MockRenderer,
        ws: MockWebSocket,
        ws2: MockWebSocket,
    ) -> None:
        reg.add(ListItem('testG', project=ListItemProject('grocery', ListItemProjectType.checklist)))
        reg.add(ListItem('testGP', project=ListItemProject('grocery.produce', ListItemProjectType.checklist)))
        await updater.subscribe(ws, ListItemProject('grocery.produce', ListItemProjectType.checklist), renderer)
        await updater.subscribe(ws2, ListItemProject('grocery.produce', ListItemProjectType.checklist), renderer)

        await updater.broadcast_update(ListItemProject('grocery.produce', ListItemProjectType.checklist))
        result = ws.spy_sent_text()
        result2 = ws.spy_sent_text()

        assert len(renderer.calls) == 1
        assert result == result2 == '+^grocery.produce:testGP'

    async def test_two_subcribers_can_have_different_renderers(
        self,
        reg: ListRegistry,
        updater: WebSocketListUpdater,
        renderer: MockRenderer,
        ws: MockWebSocket,
        ws2: MockWebSocket,
    ) -> None:
        reg.add(ListItem('testG', project=ListItemProject('grocery', ListItemProjectType.checklist)))
        reg.add(ListItem('testGP', project=ListItemProject('grocery.produce', ListItemProjectType.checklist)))
        reg.add(ListItem('testGP2', project=ListItemProject('grocery.produce', ListItemProjectType.checklist)))
        await updater.subscribe(ws, ListItemProject('grocery.produce', ListItemProjectType.checklist), renderer)

        def other_renderer(project: ListItemProject, items: list[ListItem]):
            return str(project) + ':' + ';'.join([item.description for item in items])

        await updater.subscribe(ws2, ListItemProject('grocery.produce', ListItemProjectType.checklist), other_renderer)

        await updater.broadcast_update(ListItemProject('grocery.produce', ListItemProjectType.checklist))
        result = ws.spy_sent_text()
        result2 = ws2.spy_sent_text()

        assert result != result2
        assert result == '+^grocery.produce:testGP,testGP2'
        assert result2 == '+^grocery.produce:testGP;testGP2'
