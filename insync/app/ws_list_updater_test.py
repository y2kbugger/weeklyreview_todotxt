from typing import Any

import pytest
from fastapi import WebSocket
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

    def __call__(self, items: list[ListItem]):
        self.calls.append(items)
        return ','.join([item.description for item in items])


@pytest.fixture
def renderer() -> MockRenderer:
    return MockRenderer()


class MockWebSocket:
    client_state = WebSocketState.CONNECTED

    def __init__(self):
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
def ws(anyio_backend: tuple[str, dict[str, Any]]) -> MockWebSocket:
    return MockWebSocket()


def test_can_render_channel_subscription(
    reg: ListRegistry,
    updater: WebSocketListUpdater,
    renderer: MockRenderer,
) -> None:
    item = ListItem('test1A')
    reg.add(item)
    updater.register_project_channel(item.project, renderer)

    result = updater.render_channel(item.project)

    assert len(renderer.calls) == 1
    assert result == 'test1A'


def test_when_rendered_only_matched_item_included(
    reg: ListRegistry,
    updater: WebSocketListUpdater,
    renderer: MockRenderer,
) -> None:
    reg.add(ListItem('test'))
    reg.add(ListItem('testT', project=ListItemProject('travel', ListItemProjectType.checklist)))
    reg.add(ListItem('testG', project=ListItemProject('grocery', ListItemProjectType.checklist)))
    project = ListItemProject('grocery', ListItemProjectType.checklist)
    updater.register_project_channel(project, renderer)

    result = updater.render_channel(project)

    assert len(renderer.calls) == 1
    assert result == 'testG'


def test_can_project_channel_gets_all_with_matching_root_project(
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
    updater.register_project_channel(project, renderer)

    result = updater.render_channel(project)

    # 2c is excluded because it's a different checklist
    # 4b is excluded because it's not a checklist
    assert result == 'test2A,test3A'


def test_projects_can_be_a_subset(
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
    updater.register_project_channel(project_grocery, renderer)

    project_gro = ListItemProject('gro', ListItemProjectType.checklist)
    updater.register_project_channel(project_gro, renderer)

    # Act
    result_grocery = updater.render_channel(project_grocery)
    result_gro = updater.render_channel(project_gro)

    # Assert
    assert result_grocery == 't1,t2'
    assert result_gro == 't3'


async def test_broadcast_to_channel(
    reg: ListRegistry,
    updater: WebSocketListUpdater,
    renderer: MockRenderer,
    ws: MockWebSocket,
) -> None:
    item = ListItem('test1A')
    reg.add(item)
    _ws: WebSocket = ws  # type: ignore
    await updater.subscribe(_ws, NullListItemProject(), renderer)

    await updater.broadcast_update(NullListItemProject())
    result = ws.spy_sent_text()

    assert len(renderer.calls) == 1
    assert result == 'test1A'
