from insync.db import ListDB


def test_instantiate() -> None:
    db = ListDB(':memory:')
    assert db is not None


def test_ensure_tables_created_is_idempotent() -> None:
    db = ListDB(':memory:')
    db.ensure_tables_created()
    db.ensure_tables_created()


def test_can_retrieve_empty_list() -> None:
    db = ListDB(':memory:')
    db.ensure_tables_created()
    reg = db.load()
    assert len(reg.items) == 0
