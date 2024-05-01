import pytest
from uuid6 import UUID

from insync.listregistry import NullCommand, UndoView


@pytest.fixture
def empty_undoview() -> UndoView:
    return UndoView([], [])


def test_undocommand_is_none_when_undostack_empty(empty_undoview: UndoView) -> None:
    assert empty_undoview.undocommand is None


def test_redocommand_is_none_when_redostack_empty(empty_undoview: UndoView) -> None:
    assert empty_undoview.redocommand is None


def test_undocommand_is_last_command_in_undostack() -> None:
    undostack = [
        NullCommand(UUID(int=1)),
        NullCommand(UUID(int=2)),
        NullCommand(UUID(int=3)),
    ]
    undoview = UndoView(undostack, [])
    assert undoview.undocommand == undostack[-1]
    assert undoview.redocommand is None


def test_redocommand_is_last_command_in_redostack() -> None:
    redostack = [
        NullCommand(UUID(int=1)),
        NullCommand(UUID(int=2)),
        NullCommand(UUID(int=3)),
    ]
    undoview = UndoView([], redostack)
    assert undoview.redocommand == redostack[-1]
    assert undoview.undocommand is None
