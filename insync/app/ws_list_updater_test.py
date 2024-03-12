import pytest

from insync.app.ws_list_updater import WebsocketListUpdater
from insync.listregistry import ListItem, ListItemProject, ListItemProjectType, ListRegistry


class MockWebSocket:
    pass


@pytest.fixture
def reg() -> ListRegistry:
    reg = ListRegistry()
    reg.add(ListItem('test1A'))
    reg.add(ListItem('test2C', project=ListItemProject('travel', ListItemProjectType.checklist)))
    reg.add(ListItem('test2A', project=ListItemProject('grocery', ListItemProjectType.checklist)))
    reg.add(ListItem('test3A', project=ListItemProject('grocery.produce', ListItemProjectType.checklist)))
    reg.add(ListItem('test4B', project=ListItemProject('grocery.camping', ListItemProjectType.todo)))
    reg.add(ListItem('test3B'))
    return reg


def test_can_initialize(reg: ListRegistry) -> None:
    WebsocketListUpdater(reg)


def test_can_register_subscription(reg: ListRegistry) -> None:
    updater = WebsocketListUpdater(reg)

    updater.register_channel('test', lambda x: 'test', lambda x: True)


def test_can_render_subscriptions(reg: ListRegistry) -> None:
    updater = WebsocketListUpdater(reg)
    updater.register_channel('test', lambda x: str(len(x)), lambda x: True)

    result = updater.render_channel('test')

    assert result == '6'


def test_can_filter_subscriptions(reg: ListRegistry) -> None:
    updater = WebsocketListUpdater(reg)
    updater.register_channel('test', lambda x: str(len(x)), lambda x: 'A' in x.description)

    result = updater.render_channel('test')

    assert result == '3'


def test_can_project_subscriptions_gets_all_with_matching_root_project(reg: ListRegistry) -> None:
    updater = WebsocketListUpdater(reg)
    project = ListItemProject('grocery', ListItemProjectType.checklist)
    updater.register_project_channel(project, lambda x: '\n'.join([item.description for item in x]))

    result = updater.render_channel('+^grocery')

    # 2c is excluded because it's a different checklist
    # 4b is excluded because it's not a checklist
    assert result == 'test2A\ntest3A'
