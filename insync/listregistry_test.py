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
    UndoView,
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


def test_registry_can_return_undoview(reg: ListRegistry, item: ListItem) -> None:
    undoview = reg.undoview()
    assert isinstance(undoview, UndoView)
    assert undoview.undocommand is None
    assert undoview.redocommand is None
    cmd = ArchiveCommand(item.uuid, True)
    reg.do(cmd)
    assert undoview.undocommand is cmd


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

    def test_do(self, reg: ListRegistry, cmd: Command) -> None:
        cmd.do(reg)
        assert cmd.done

    def test_undo(self, reg: ListRegistry, cmd: Command) -> None:
        cmd.do(reg)
        cmd.undo(reg)
        assert not cmd.done

    def test_undo_before_do(self, reg: ListRegistry, cmd: Command) -> None:
        with pytest.raises(AssertionError):
            cmd.undo(reg)

    def test_redo(self, reg: ListRegistry, cmd: Command) -> None:
        cmd.do(reg)
        cmd.undo(reg)
        cmd.do(reg)
        assert cmd.done

    def test_double_do(self, reg: ListRegistry, cmd: Command) -> None:
        cmd.do(reg)
        with pytest.raises(AssertionError):
            cmd.do(reg)
        assert cmd.done
        with pytest.raises(AssertionError):
            # make sure repeated attempts continue to fail
            cmd.do(reg)
        assert cmd.done

    def test_double_undo(self, reg: ListRegistry, cmd: Command) -> None:
        cmd.do(reg)
        cmd.undo(reg)
        with pytest.raises(AssertionError):
            cmd.undo(reg)
        assert not cmd.done
        with pytest.raises(AssertionError):
            # make sure repeated attempts continue to fail
            cmd.undo(reg)
        assert not cmd.done


def test_registry_excepts_when_trying_to_undo_nothing(reg: ListRegistry) -> None:
    with pytest.raises(IndexError):
        reg.undo()


def test_registry_undoes_last_command(reg: ListRegistry, item: ListItem) -> None:
    reg.do(ArchiveCommand(item.uuid, True))
    reg.do(CompletionCommand(item.uuid, True))
    assert item.completed
    reg.undo()
    assert not item.completed


def test_registry_pops_undone_command_off_redostack(reg: ListRegistry, item: ListItem) -> None:
    reg.do(CompletionCommand(item.uuid, True))
    reg.undo()
    with pytest.raises(IndexError):
        reg.undo()


def test_registry_excepts_when_trying_to_redo_nothing(reg: ListRegistry) -> None:
    with pytest.raises(IndexError):
        reg.redo()


def test_registry_redoes_last_undone_command(reg: ListRegistry, item: ListItem) -> None:
    reg.do(CompletionCommand(item.uuid, True))
    assert item.completed
    reg.undo()
    assert not item.completed
    reg.redo()
    assert item.completed


def test_registry_redo_puts_command_back_on_undostack(reg: ListRegistry, item: ListItem) -> None:
    reg.do(CompletionCommand(item.uuid, True))
    reg.undo()
    reg.redo()
    reg.undo()
    assert not item.completed


def test_registry_pops_redone_command_off_redostack(reg: ListRegistry, item: ListItem) -> None:
    reg.do(CompletionCommand(item.uuid, True))
    reg.undo()
    reg.redo()
    with pytest.raises(IndexError):
        reg.redo()


def test_doing_command_clears_redostack(reg: ListRegistry, item: ListItem) -> None:
    reg.do(CompletionCommand(item.uuid, True))
    reg.undo()
    reg.do(ArchiveCommand(item.uuid, True))
    assert not item.completed
    with pytest.raises(IndexError):
        reg.redo()


#### COMMAND SPECIFIC TESTS ####
def test_can_create_item_using_command(reg: ListRegistry) -> None:
    new_item = ListItem('test')
    old_len = len(reg)

    reg.do(CreateCommand(new_item.uuid, new_item))

    assert len(reg) == old_len + 1
    assert new_item in reg


def test_can_undo_create_item(reg: ListRegistry) -> None:
    new_item = ListItem('test')
    old_len = len(reg)
    reg.do(CreateCommand(new_item.uuid, new_item))

    reg.undo()

    assert len(reg) == old_len
    assert new_item not in reg


def test_can_complete_item(reg: ListRegistry, item: ListItem) -> None:
    item.completion_datetime = None
    assert not item.completed

    reg.do(cc := CompletionCommand(item.uuid, True))

    assert item.completed
    assert item.completion_datetime == cc.completion_datetime_new


def test_can_undo_completion(reg: ListRegistry, item: ListItem) -> None:
    item.completion_datetime = None
    reg.do(CompletionCommand(item.uuid, True))
    assert item.completed

    reg.undo()

    assert not item.completed
    assert item.completion_datetime is None


def test_can_uncomplete_item(reg: ListRegistry, item: ListItem) -> None:
    item.completion_datetime = dt.datetime.now(tz=dt.timezone.utc)
    assert item.completed

    reg.do(CompletionCommand(item.uuid, False))

    assert not item.completed


def test_can_archive_item(reg: ListRegistry, item: ListItem) -> None:
    item.archival_datetime = None
    assert not item.archived

    reg.do(ac := ArchiveCommand(item.uuid, True))

    assert item.archived
    assert item.archival_datetime == ac.archival_datetime_new


def test_can_unarchive_item(reg: ListRegistry, item: ListItem) -> None:
    item.archival_datetime = dt.datetime.now(tz=dt.timezone.utc)
    assert item.archived

    reg.do(ArchiveCommand(item.uuid, False))

    assert not item.archived


def test_can_undo_archival(reg: ListRegistry, item: ListItem) -> None:
    reg.do(ArchiveCommand(item.uuid, True))
    assert item.archived

    reg.undo()

    assert not item.archived
    assert item.archival_datetime is None


def test_reset_raises_when_not_a_checklist(reg: ListRegistry, item: ListItem) -> None:
    with pytest.raises(AssertionError):
        reg.do(ChecklistResetCommand(item.project))


def test_reset_checklist_doesnt_archive_active(reg: ListRegistry, item: ListItem) -> None:
    item.project = ListItemProject('grocery', ListItemProjectType.checklist)
    item.completion_datetime = None
    assert not item.archived

    reg.do(ChecklistResetCommand(item.project))

    assert not item.archived


def test_reset_checklist_archives_completed(reg: ListRegistry, item: ListItem) -> None:
    item.project = ListItemProject('grocery', ListItemProjectType.checklist)
    item.completion_datetime = dt.datetime.now(tz=dt.timezone.utc)
    assert item.completed
    assert not item.archived

    reg.do(ChecklistResetCommand(item.project))

    assert item.completed
    assert item.archived


def test_reset_checklist_does_not_affect_other_projects(reg: ListRegistry, item: ListItem) -> None:
    item.project = ListItemProject('grocery', ListItemProjectType.checklist)
    item.completion_datetime = dt.datetime.now(tz=dt.timezone.utc)
    assert not item.archived

    reg.do(ChecklistResetCommand(ListItemProject('travel', ListItemProjectType.checklist)))

    assert not item.archived


def test_reset_checklist_resets_subprojects(reg: ListRegistry, item: ListItem) -> None:
    item.project = ListItemProject('grocery.produce', ListItemProjectType.checklist)
    item.completion_datetime = dt.datetime.now(tz=dt.timezone.utc)
    assert not item.archived

    reg.do(ChecklistResetCommand(ListItemProject('grocery', ListItemProjectType.checklist)))

    assert item.archived


def test_reset_checklist_uncompletes_recurring_items_instead_of_archiving(reg: ListRegistry, item: ListItem) -> None:
    item.project = ListItemProject('grocery', ListItemProjectType.checklist)
    item.completion_datetime = dt.datetime.now(tz=dt.timezone.utc)
    item.recurring = True
    assert item.completed
    assert not item.archived

    reg.do(ChecklistResetCommand(item.project))

    assert not item.completed
    assert not item.archived


def test_can_undo_reset_checklist_archive(reg: ListRegistry, item: ListItem) -> None:
    item.project = ListItemProject('grocery', ListItemProjectType.checklist)
    item.completion_datetime = dt.datetime.now(tz=dt.timezone.utc)

    reg.do(ChecklistResetCommand(item.project))
    assert item.completed
    assert item.archived

    reg.undo()

    assert item.completed
    assert not item.archived


def test_can_undo_reset_checklist_recur(reg: ListRegistry, item: ListItem) -> None:
    item.project = ListItemProject('grocery', ListItemProjectType.checklist)
    item.completion_datetime = dt.datetime.now(tz=dt.timezone.utc)
    item.recurring = True

    reg.do(ChecklistResetCommand(item.project))
    assert not item.completed
    assert not item.archived

    reg.undo()

    assert not item.archived
    assert item.completed


def test_can_mark_item_as_recurring(reg: ListRegistry, item: ListItem) -> None:
    assert not item.recurring

    reg.do(RecurringCommand(item.uuid, True))

    assert item.recurring


def test_can_unmark_item_as_recurring(reg: ListRegistry, item: ListItem) -> None:
    item.recurring = True
    assert item.recurring

    reg.do(RecurringCommand(item.uuid, False))

    assert not item.recurring


def test_can_undo_mark_as_recurring(reg: ListRegistry, item: ListItem) -> None:
    reg.do(RecurringCommand(item.uuid, True))
    assert item.recurring

    reg.undo()

    assert not item.recurring
