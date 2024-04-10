import datetime as dt

import pytest

from insync.listitem import (
    ListItem,
    ListItemProject,
    ListItemProjectType,
)


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


@pytest.fixture
def item() -> ListItem:
    return ListItem('test')


def test_imcomplete_is_the_default(item: ListItem) -> None:
    assert not item.completed


def test_items_are_not_archived_by_default(item: ListItem) -> None:
    assert not item.archived


def test_items_are_created_with_a_creation_datetime(item: ListItem) -> None:
    assert isinstance(item.creation_datetime, dt.datetime)


def test_completion_datetime_drives_completed(item: ListItem) -> None:
    item.completion_datetime = dt.datetime.now(tz=dt.timezone.utc)
    assert item.completed


def test_completion_datetime_of_none_is_not_completed(item: ListItem) -> None:
    item.completion_datetime = None
    assert not item.completed


def test_archival_datetime_drives_archived(item: ListItem) -> None:
    item.archival_datetime = dt.datetime.now(tz=dt.timezone.utc)
    assert item.archived


def test_archival_datetime_of_none_is_not_archived(item: ListItem) -> None:
    item.archival_datetime = None
    assert not item.archived
