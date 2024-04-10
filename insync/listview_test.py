import datetime as dt

from insync.listitem import ListItem
from insync.listview import ListView


def test_can_create_view() -> None:
    ListView([])


def test_can_add_item_to_view() -> None:
    item = ListItem('test')
    items = [item]
    view = ListView(items)

    assert item in view

def test_archived_item_is_not_in_items() -> None:
    active_item = ListItem('test')
    archived_item = ListItem('test', archival_datetime=dt.datetime.now(tz=dt.timezone.utc))
    items = [archived_item, active_item]
    view = ListView(items)

    assert archived_item not in view.active_items
    assert archived_item in view.archived_items

    assert active_item in view.active_items
    assert active_item not in view.archived_items
