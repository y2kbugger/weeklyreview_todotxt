from insync.listitem import (
    ListItem,
    ListItemProject,
    ListItemProjectType,
)


def test_instantiate_listitem() -> None:
    item = ListItem('test')
    assert item.description == 'test'


def test_instantiate_listitem_with_project() -> None:
    itemproject = ListItemProject('grocery', ListItemProjectType.checklist)
    item = ListItem('test', project=itemproject)
    assert item.project.name == 'grocery'


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
