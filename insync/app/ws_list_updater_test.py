
import pytest

from insync.app.ws_list_updater import WebsocketListUpdater
from insync.listregistry import ListItem, ListItemProject, ListItemProjectType, ListRegistry, NullListItemProject


@pytest.fixture
def reg() -> ListRegistry:
    return ListRegistry()


@pytest.fixture
def updater(reg: ListRegistry) -> WebsocketListUpdater:
    return WebsocketListUpdater(reg)


class MockRenderer:
    def __init__(self):
        self.calls = []

    def __call__(self, items: list[ListItem]):
        self.calls.append(items)
        return ','.join([item.description for item in items])


@pytest.fixture
def renderer() -> MockRenderer:
    return MockRenderer()


# class MockWebSocket(Protocol):
class MockWebSocket:
    pass


@pytest.fixture
def ws() -> MockWebSocket:
    return MockWebSocket()


def test_can_render_channel_subscription(
    reg: ListRegistry,
    updater: WebsocketListUpdater,
    renderer: MockRenderer,
) -> None:
    reg.add(ListItem('test1A'))
    updater.register_project_channel(NullListItemProject(), renderer)

    result = updater.render_channel(NullListItemProject())

    assert len(renderer.calls) == 1
    assert result == 'test1A'


def test_when_rendered_only_matched_item_included(
    reg: ListRegistry,
    updater: WebsocketListUpdater,
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
    updater: WebsocketListUpdater,
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
    updater: WebsocketListUpdater,
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
