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


class TestCanFindCommonProjectRoot:
    def test_root_of_no_projects_is_null(self) -> None:
        assert ListItemProject.common_root([]) == ListItemProject('', ListItemProjectType.null)

    def test_root_of_one_project_is_itself(self) -> None:
        project = ListItemProject('grocery.produce', ListItemProjectType.checklist)
        assert ListItemProject.common_root([project]) == ListItemProject('grocery.produce', ListItemProjectType.checklist)

    def test_common_root_can_be_empty(self) -> None:
        project1 = ListItemProject('grocery.produce', ListItemProjectType.checklist)
        project2 = ListItemProject('dairy', ListItemProjectType.checklist)
        assert ListItemProject.common_root([project1, project2]) == ListItemProject('', ListItemProjectType.checklist)

    def test_root_of_projects_with_different_types_is_null(self) -> None:
        project1 = ListItemProject('grocery.produce', ListItemProjectType.checklist)
        project2 = ListItemProject('grocery.produce', ListItemProjectType.todo)
        assert ListItemProject.common_root([project1, project2]) == ListItemProject('', ListItemProjectType.null)

    def test_root_of_projects_with_same_type_is_common_prefix(self) -> None:
        project1 = ListItemProject('grocery.produce', ListItemProjectType.checklist)
        project2 = ListItemProject('grocery.dairy', ListItemProjectType.checklist)
        assert ListItemProject.common_root([project1, project2]) == ListItemProject('grocery', ListItemProjectType.checklist)

    def test_common_root_can_be_deeper_than_one_level(self) -> None:
        project1 = ListItemProject('grocery.produce.fruit', ListItemProjectType.checklist)
        project2 = ListItemProject('grocery.produce.vegetable', ListItemProjectType.checklist)
        assert ListItemProject.common_root([project1, project2]) == ListItemProject('grocery.produce', ListItemProjectType.checklist)

    def test_commmon_root_early_return_ok(self) -> None:
        p1 = ListItemProject('a.grocery.produce.fruit', ListItemProjectType.checklist)
        p2 = ListItemProject('a.grocery.produce.fruit.dsf', ListItemProjectType.checklist)
        p3 = ListItemProject('a.grocery.produce.vegetable', ListItemProjectType.checklist)
        p4 = ListItemProject('a.porridge.lol.sdaflasdf.asdf', ListItemProjectType.checklist)
        print(ListItemProject.common_root([p1, p2, p3, p4]))
        assert ListItemProject.common_root([p1, p2, p3, p4]) == ListItemProject('a', ListItemProjectType.checklist)


def test_truncate_project() -> None:
    project = ListItemProject('grocery.produce.fruit', ListItemProjectType.checklist)
    assert project.truncate(0) == ListItemProject('', ListItemProjectType.checklist)
    assert project.truncate(1) == ListItemProject('grocery', ListItemProjectType.checklist)
    assert project.truncate(2) == ListItemProject('grocery.produce', ListItemProjectType.checklist)
    assert project.truncate(3) == ListItemProject('grocery.produce.fruit', ListItemProjectType.checklist)
    assert project.truncate(4) == ListItemProject('grocery.produce.fruit', ListItemProjectType.checklist)


def test_project_len() -> None:
    assert len(ListItemProject('grocery.produce.fruit', ListItemProjectType.checklist)) == 3
    assert len(ListItemProject('grocery.produce', ListItemProjectType.checklist)) == 2
    assert len(ListItemProject('grocery', ListItemProjectType.checklist)) == 1
    assert len(ListItemProject('', ListItemProjectType.checklist)) == 0


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
