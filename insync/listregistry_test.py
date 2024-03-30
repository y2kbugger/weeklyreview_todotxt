import datetime as dt

from insync.listregistry import ArchiveCommand, ChecklistResetCommand, CompletionCommand, CreateCommand, ListItem, ListItemProject, ListItemProjectType, ListRegistry


def test_instantiate_listitem() -> None:
    item = ListItem('test')
    assert item.description == 'test'


def test_instantiate_listitem_with_project() -> None:
    itemproject = ListItemProject('grocery', ListItemProjectType.checklist)
    item = ListItem('test', project=itemproject)
    assert item.project.name == 'grocery'


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
    item = ListItem('test', completion_datetime=dt.datetime.now())
    reg.add(item)
    assert item.completed

    reg.do(CompletionCommand(item.uuid, False))

    assert not item.completed


def test_can_create_item_using_command() -> None:
    reg = ListRegistry()
    item = ListItem('test')

    reg.do(CreateCommand(item.uuid, item))

    assert len(list(reg.items)) == 1
    assert item in reg.items


def test_can_undo_create_item() -> None:
    reg = ListRegistry()
    item = ListItem('test')
    reg.do(CreateCommand(item.uuid, item))

    reg.undo()

    assert len(list(reg.items)) == 0
    assert item not in reg.items

def test_can_archive_item() -> None:
    reg = ListRegistry()
    item = ListItem('test')
    reg.add(item)
    assert not item.archived

    reg.do(ArchiveCommand(item.uuid, True))

    assert item.archived

def test_can_reset_checklist() -> None:
    reg = ListRegistry()
    item1 = ListItem('test1', project=ListItemProject('grocery', ListItemProjectType.checklist))
    item2 = ListItem('test2', project=ListItemProject('grocery', ListItemProjectType.checklist))
    reg.add(item1)
    reg.add(item2)
    reg.do(CompletionCommand(item1.uuid, True))

    reg.do(ChecklistResetCommand(ListItemProject('grocery', ListItemProjectType.checklist)))

    assert item1.archived
    assert item1.completed
    assert not item2.archived
    assert not item2.completed


def test_archived_item_is_not_in_items() -> None:
    reg = ListRegistry()
    item = ListItem('test')
    reg.add(item)
    reg.do(ArchiveCommand(item.uuid, True))

    assert item not in reg.items


def test_can_undo_archival() -> None:
    reg = ListRegistry()
    item = ListItem('test')
    reg.add(item)
    reg.do(ArchiveCommand(item.uuid, True))

    reg.undo()

    assert not item.archived


class TestProjectCanContainProject:
    def test_different_types_never_are_never_contained(self) -> None:
        assert ListItemProject('grocery', ListItemProjectType.checklist) not in ListItemProject('grocery', ListItemProjectType.todo)

    def test_project_is_contained_in_itself(self) -> None:
        assert ListItemProject('grocery', ListItemProjectType.checklist) in ListItemProject('grocery', ListItemProjectType.checklist)

    def test_project_is_contained_in_its_parent(self) -> None:
        assert ListItemProject('grocery.produce', ListItemProjectType.checklist) in ListItemProject('grocery', ListItemProjectType.checklist)

    def test_project_is_not_contained_in_its_child(self) -> None:
        assert ListItemProject('grocery', ListItemProjectType.checklist) not in ListItemProject('grocery.produce', ListItemProjectType.checklist)

    def test_project_is_not_contained_in_different_project(self) -> None:
        assert ListItemProject('apples', ListItemProjectType.todo) not in ListItemProject('bananas', ListItemProjectType.todo)

    def test_project_is_contained_in_root_if_type_is_same(self) -> None:
        assert ListItemProject('grocery', ListItemProjectType.checklist) in ListItemProject('', ListItemProjectType.checklist)

    def test_project_is_not_contained_in_root_if_type_is_different(self) -> None:
        assert ListItemProject('grocery', ListItemProjectType.checklist) not in ListItemProject('', ListItemProjectType.todo)

    def test_any_project_is_contained_in_root_if_type_is_null(self) -> None:
        assert ListItemProject('grocery', ListItemProjectType.checklist) in ListItemProject('', ListItemProjectType.null)
        assert ListItemProject('apples', ListItemProjectType.todo) in ListItemProject('', ListItemProjectType.null)
        assert ListItemProject('', ListItemProjectType.todo) in ListItemProject('', ListItemProjectType.null)
        assert ListItemProject('', ListItemProjectType.null) in ListItemProject('', ListItemProjectType.null)

    def test_null_project_is_not_contained_in_any_other_project(self) -> None:
        assert ListItemProject('', ListItemProjectType.null) not in ListItemProject('grocery', ListItemProjectType.checklist)
        assert ListItemProject('', ListItemProjectType.null) not in ListItemProject('grocery.produce', ListItemProjectType.checklist)
        assert ListItemProject('', ListItemProjectType.null) not in ListItemProject('apples', ListItemProjectType.todo)
        assert ListItemProject('', ListItemProjectType.null) not in ListItemProject('', ListItemProjectType.todo)
        assert ListItemProject('', ListItemProjectType.null) not in ListItemProject('', ListItemProjectType.checklist)

    def test_project_name_parts(self) -> None:
        project = ListItemProject('grocery.produce', ListItemProjectType.checklist)
        assert project.name_parts == ['grocery', 'produce']

    def test_project_name_parts_of_root(self) -> None:
        project = ListItemProject('', ListItemProjectType.checklist)
        assert project.name_parts == []

    def test_project_name_part_can_be_substring_of_completely_different_project(self) -> None:
        assert ListItemProject('gro', ListItemProjectType.checklist) not in ListItemProject('grocery', ListItemProjectType.checklist)
        assert ListItemProject('grocery', ListItemProjectType.checklist) not in ListItemProject('gro', ListItemProjectType.checklist)
