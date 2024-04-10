from insync.listitem import ListItem
from insync.listview import ListView


def test_can_create_view() -> None:
    ListView([])


def test_can_add_item_to_view() -> None:
    item = ListItem('test')
    items = [item]
    view = ListView(items)
    assert item in view
