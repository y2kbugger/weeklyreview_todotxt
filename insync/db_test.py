import datetime as dt
from collections.abc import Iterable

import pytest

from insync.db import ListDB
from insync.listitem import ListItem, ListItemPriority, ListItemProject, ListItemProjectType
from insync.listregistry import ListRegistry


@pytest.fixture()
def db() -> Iterable[ListDB]:
    _db = ListDB(':memory:')
    _db.ensure_tables_created()
    yield _db
    _db.close()


def test_instantiate(db: ListDB) -> None:
    assert db is not None


def test_prexisting_tables_doesnt_raise(db: ListDB) -> None:
    db.ensure_tables_created()


def test_can_retrieve_empty_list(db: ListDB) -> None:
    reg = db.load()
    assert len(list(reg)) == 0


@pytest.mark.parametrize(
    'item',
    [
        ListItem('test'),
        ListItem('test', priority=ListItemPriority("K")),
        ListItem('test', project=ListItemProject('grocery', ListItemProjectType.checklist)),
        ListItem('test', completion_datetime=dt.datetime.now(tz=dt.timezone.utc)),
        ListItem('test', archival_datetime=dt.datetime.now(tz=dt.timezone.utc)),
        ListItem('test', creation_datetime=dt.datetime.now(tz=dt.timezone.utc) - dt.timedelta(days=1)),
        ListItem('test', recurring=True),
    ],
)
def test_can_retrieve_persisted_item_with_project(db: ListDB, item: ListItem) -> None:
    reg = ListRegistry()
    reg.add(item)
    db.patch(reg)

    reg2 = db.load()
    items2 = list(reg)

    assert len(list(reg2)) == 1
    assert item == items2[0]


def test_trying_to_save_naive_datetime_raises(db: ListDB) -> None:
    reg = ListRegistry()
    item = ListItem('test', completion_datetime=dt.datetime.now())
    reg.add(item)
    with pytest.raises(AssertionError):
        db.patch(reg)
