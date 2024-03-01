from collections.abc import Iterable

import pytest

from insync.db import ListDB
from insync.list import ListItem, ListRegistry


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
    assert len(list(reg.items)) == 0


def test_can_retrieve_persisted_item(db: ListDB) -> None:
    reg = ListRegistry()
    item = ListItem('test')
    reg.add(item)
    db.patch(reg)

    reg2 = db.load()
    item2 = next(iter(reg2.items))

    assert len(list(reg2.items)) == 1
    assert item2.description == 'test'
    assert not item2.completed
    assert item == item2
