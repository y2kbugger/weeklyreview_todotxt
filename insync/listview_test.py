import datetime as dt

from insync.listitem import ListItem, ListItemProject, ListItemProjectType, NullListItemProject
from insync.listview import ListView


def test_can_create_view() -> None:
    ListView([], NullListItemProject())


def test_can_add_item_to_view() -> None:
    item = ListItem('test')
    items = [item]
    view = ListView(items, item.project)

    assert item in view


def test_active_and_archived_are_split() -> None:
    active_item = ListItem('test')
    archived_item = ListItem('test', archival_datetime=dt.datetime.now(tz=dt.timezone.utc))
    items = [archived_item, active_item]
    view = ListView(items, active_item.project)

    assert archived_item not in view.active_items
    assert archived_item in view.archived_items

    assert active_item in view.active_items
    assert active_item not in view.archived_items


def test_bysubproject_returns_view_of_grouped_items() -> None:
    item2 = ListItem('test2', project=ListItemProject('projectA.produce', ListItemProjectType.checklist))
    item3 = ListItem('test3', project=ListItemProject('projectA.produce', ListItemProjectType.checklist))

    items = [item2, item3]
    view = ListView(items, ListItemProject('projectA', ListItemProjectType.checklist))
    subprojectviews = list(view.group_by_subproject())
    assert len(subprojectviews) == 1
    assert isinstance(subprojectviews[0], ListView)
    assert subprojectviews[0].project == ListItemProject('projectA.produce', ListItemProjectType.checklist)


def test_bysubproject_groups_only_next_layer() -> None:
    item2 = ListItem('test2', project=ListItemProject('projectA.produce', ListItemProjectType.checklist))
    item3 = ListItem('test3', project=ListItemProject('projectA.produce.fruits', ListItemProjectType.checklist))

    items = [item2, item3]
    view = ListView(items, ListItemProject('projectA', ListItemProjectType.checklist))
    subprojectviews = list(view.group_by_subproject())
    assert len(subprojectviews) == 1
    assert subprojectviews[0].project == ListItemProject('projectA.produce', ListItemProjectType.checklist)


def test_bysubproject_include_group_of_items_of_merely_self() -> None:
    item1 = ListItem('test1', project=ListItemProject('projectA', ListItemProjectType.checklist))
    item2 = ListItem('test2', project=ListItemProject('projectA.produce', ListItemProjectType.checklist))

    items = [item1, item2]
    view = ListView(items, ListItemProject('projectA', ListItemProjectType.checklist))
    subprojectviews = list(view.group_by_subproject())
    subprojects = [view.project for view in subprojectviews]
    assert len(subprojectviews) == 2
    assert ListItemProject('projectA', ListItemProjectType.checklist) in subprojects
    assert ListItemProject('projectA.produce', ListItemProjectType.checklist) in subprojects


def test_bysubproject_include_group_of_items_of_merely_self_as_first_group() -> None:
    items1 = [ListItem('t', project=ListItemProject(f'projectA.a{n}', ListItemProjectType.checklist)) for n in range(20)]
    item1 = ListItem('test1', project=ListItemProject('projectA', ListItemProjectType.checklist))
    items2 = [ListItem('t', project=ListItemProject(f'projectA.b{n}', ListItemProjectType.checklist)) for n in range(20)]
    items = [*items1, item1, *items2]
    view = ListView(items, ListItemProject('projectA', ListItemProjectType.checklist))
    subprojectviews = list(view.group_by_subproject())
    subprojects = [view.project for view in subprojectviews]

    assert subprojects[0] == ListItemProject('projectA', ListItemProjectType.checklist)


# handle when project of original listview is '' and null
#  this would include all items of every project in registry
#  should be grouped by project('', checklist) and project('', todo), etc
# handle when project of original listview is '' but also checklist
#  this is like next level after the above
# should group by root project for a given type ('grocery', checklist) and project('work', checklist)
