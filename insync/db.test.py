from typing import Iterator

import pytest

from insync.db import ListDB


@pytest.fixture()
def db() -> Iterator[ListDB]:
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
    assert len(reg.items) == 0
