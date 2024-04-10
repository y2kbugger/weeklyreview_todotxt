import datetime as dt

import pytest

from insync.listitem import (
    ListItem,
    ListItemProject,
    ListItemProjectType,
    NullListItemProject,
)
from insync.listregistry import (
    ArchiveCommand,
    ChecklistResetCommand,
    Command,
    CompletionCommand,
    CreateCommand,
    ListRegistry,
    RecurringCommand,
)
from insync.listview import ListView


@pytest.fixture
def item() -> ListItem:
    return ListItem('test')

@pytest.fixture
def reg(item: ListItem) -> ListRegistry:
    _reg = ListRegistry()
    _reg.add(item)
    return _reg

def test_registry_can_return_view(reg: ListRegistry) -> None:
    view = reg.search(project=NullListItemProject())
    assert isinstance(view, ListView)


command_makers = [
    (lambda item: ArchiveCommand(item.uuid, True), 'ArchiveCommand'),
    (lambda item: ChecklistResetCommand(ListItemProject('grocery', ListItemProjectType.checklist)), 'ChecklistResetCommand'),
    (lambda item: CompletionCommand(item.uuid, True), 'CompletionCommand'),
    (lambda item: CreateCommand(item.uuid, item), 'CreateCommand'),
    (lambda item: RecurringCommand(item.uuid, True), 'ArchiveCommand'),
]

@pytest.fixture(params=[cm[0] for cm in command_makers], ids=[cm[1] for cm in command_makers])
def cmd(request: pytest.FixtureRequest, item: ListItem) -> Command:
    return request.param(item)


class TestCommandSemantics:
    """Test the basic do/undo semantics of the base Command, other tests will test the specific behavior of each Command"""

    """
    - test each Command:
    - do
    - undo (do, undo)
    - undo before do (undo) AssertionError
    - redo (do, undo, do)
    - double do (do, do) AssertionError
    - double undo (do, undo, undo) AssertionError
    """

    def test_do(self, item: ListItem, reg: ListRegistry, cmd: Command) -> None:
        cmd.do(reg)
        assert cmd.done

    def test_undo(self, item: ListItem, reg: ListRegistry, cmd: Command) -> None:
        cmd.do(reg)
        cmd.undo(reg)
        assert not cmd.done

    def test_undo_before_do(self, item: ListItem, reg: ListRegistry, cmd: Command) -> None:
        with pytest.raises(AssertionError):
            cmd.undo(reg)

    def test_redo(self, item: ListItem, reg: ListRegistry, cmd: Command) -> None:
        cmd.do(reg)
        cmd.undo(reg)
        cmd.do(reg)
        assert cmd.done

    def test_double_do(self, item: ListItem, reg: ListRegistry, cmd: Command) -> None:
        cmd.do(reg)
        with pytest.raises(AssertionError):
            cmd.do(reg)
        assert cmd.done
        with pytest.raises(AssertionError):
            # make sure repeated attempts continue to fail
            cmd.do(reg)
        assert cmd.done

    def test_double_undo(self, item: ListItem, reg: ListRegistry, cmd: Command) -> None:
        cmd.do(reg)
        cmd.undo(reg)
        with pytest.raises(AssertionError):
            cmd.undo(reg)
        assert not cmd.done
        with pytest.raises(AssertionError):
            # make sure repeated attempts continue to fail
            cmd.undo(reg)
        assert not cmd.done


def test_can_complete_item() -> None:
    reg = ListRegistry()
    item = ListItem('test')
    reg.add(item)
    assert not item.completed

    reg.do(cc := CompletionCommand(item.uuid, True))

    assert item.completed
    assert item.completion_datetime == cc.completion_datetime_new


def test_can_undo_completion() -> None:
    reg = ListRegistry()
    item = ListItem('test')
    reg.add(item)
    reg.do(CompletionCommand(item.uuid, True))
    assert item.completed

    reg.undo()

    assert not item.completed
    assert item.completion_datetime is None


def test_can_uncomplete_item() -> None:
    reg = ListRegistry()
    item = ListItem('test', completion_datetime=dt.datetime.now(tz=dt.timezone.utc))
    reg.add(item)
    assert item.completed

    reg.do(CompletionCommand(item.uuid, False))

    assert not item.completed


def test_can_create_item_using_command() -> None:
    reg = ListRegistry()
    item = ListItem('test')

    reg.do(CreateCommand(item.uuid, item))

    assert len(reg) == 1
    assert item in reg


def test_can_undo_create_item() -> None:
    reg = ListRegistry()
    item = ListItem('test')
    reg.do(CreateCommand(item.uuid, item))

    reg.undo()

    assert len(reg) == 0
    assert item not in reg


def test_can_archive_item() -> None:
    reg = ListRegistry()
    item = ListItem('test')
    reg.add(item)
    assert not item.archived

    reg.do(ac := ArchiveCommand(item.uuid, True))

    assert item.archived
    assert item.archival_datetime == ac.archival_datetime_new


def test_can_unarchive_item() -> None:
    reg = ListRegistry()
    item = ListItem('test', archival_datetime=dt.datetime.now(tz=dt.timezone.utc))
    reg.add(item)
    assert item.archived

    reg.do(ArchiveCommand(item.uuid, False))

    assert not item.archived


def test_can_undo_archival() -> None:
    reg = ListRegistry()
    item = ListItem('test')
    reg.add(item)
    reg.do(ArchiveCommand(item.uuid, True))
    assert item.archived

    reg.undo()

    assert not item.archived
    assert item.archival_datetime is None


def test_reset_checklist_archives_completed() -> None:
    reg = ListRegistry()
    item1 = ListItem('test1', project=ListItemProject('grocery', ListItemProjectType.checklist))
    item2 = ListItem('test2', project=ListItemProject('grocery', ListItemProjectType.checklist))
    reg.add(item1)
    reg.add(item2)
    reg.do(CompletionCommand(item1.uuid, True))

    reg.do(ChecklistResetCommand(ListItemProject('grocery', ListItemProjectType.checklist)))

    assert item1.archived
    assert not item2.archived


def test_reset_checklist_does_not_affect_other_projects() -> None:
    reg = ListRegistry()
    item1 = ListItem('test1', project=ListItemProject('grocery', ListItemProjectType.checklist))
    item2 = ListItem('test2', project=ListItemProject('grocery', ListItemProjectType.todo))
    reg.add(item1)
    reg.add(item2)
    reg.do(CompletionCommand(item1.uuid, True))
    reg.do(CompletionCommand(item2.uuid, True))

    reg.do(ChecklistResetCommand(ListItemProject('grocery', ListItemProjectType.checklist)))

    assert item1.archived
    assert not item2.archived


def test_reset_checkout_resets_subprojects() -> None:
    reg = ListRegistry()
    item1 = ListItem('test1', project=ListItemProject('grocery.produce', ListItemProjectType.checklist))
    reg.add(item1)
    reg.do(CompletionCommand(item1.uuid, True))

    reg.do(ChecklistResetCommand(ListItemProject('grocery', ListItemProjectType.checklist)))

    assert item1.archived


def test_reset_checkilist_uncompletes_recurring_items() -> None:
    reg = ListRegistry()
    item1 = ListItem('test1', project=ListItemProject('grocery', ListItemProjectType.checklist), recurring=True)
    reg.add(item1)
    reg.do(CompletionCommand(item1.uuid, True))

    reg.do(ChecklistResetCommand(ListItemProject('grocery', ListItemProjectType.checklist)))

    assert not item1.completed


def test_can_undo_reset_checklist() -> None:
    reg = ListRegistry()
    item1 = ListItem('test1', project=ListItemProject('grocery', ListItemProjectType.checklist))
    item2 = ListItem('test2', project=ListItemProject('grocery', ListItemProjectType.checklist), recurring=True)
    reg.add(item1)
    reg.add(item2)
    reg.do(CompletionCommand(item1.uuid, True))
    reg.do(CompletionCommand(item2.uuid, True))

    reg.do(ChecklistResetCommand(ListItemProject('grocery', ListItemProjectType.checklist)))
    assert item1.completed
    assert item1.archived

    assert not item2.completed
    assert not item2.archived

    reg.undo()

    assert item1.completed
    assert not item1.archived

    assert not item2.archived
    assert item2.completed


def test_can_mark_item_as_recurring() -> None:
    reg = ListRegistry()
    item = ListItem('test')
    reg.add(item)
    assert not item.recurring

    reg.do(RecurringCommand(item.uuid, True))

    assert item.recurring


def test_can_unmark_item_as_recurring() -> None:
    reg = ListRegistry()
    item = ListItem('test', recurring=True)
    reg.add(item)
    assert item.recurring

    reg.do(RecurringCommand(item.uuid, False))

    assert not item.recurring


def test_can_undo_mark_as_recurring() -> None:
    reg = ListRegistry()
    item = ListItem('test')
    reg.add(item)
    reg.do(RecurringCommand(item.uuid, True))
    assert item.recurring

    reg.undo()

    assert not item.recurring
