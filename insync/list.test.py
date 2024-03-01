from insync.list import CompletionCommand, ListItem, ListRegistry


def test_add_item() -> None:
    reg = ListRegistry()
    item = ListItem('test')
    reg.add(item)
    assert len(list(reg.items)) == 1
    assert item in reg.items


def test_can_complete_item() -> None:
    reg = ListRegistry()
    item = ListItem('test')
    reg.add(item)
    assert not item.completed

    reg.do(CompletionCommand(item.uuid, True))

    assert item.completed


def test_can_undo_completion() -> None:
    reg = ListRegistry()
    item = ListItem('test')
    reg.add(item)
    reg.do(CompletionCommand(item.uuid, True))

    reg.undo()

    assert not item.completed
