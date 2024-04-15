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

    assert archived_item not in view.active
    assert archived_item in view.archived

    assert active_item in view.active
    assert active_item not in view.archived


def test_incomplete_and_complete_are_split() -> None:
    incomplete_item = ListItem('test')
    complete_item = ListItem('test', completion_datetime=dt.datetime.now(tz=dt.timezone.utc))
    items = [incomplete_item, complete_item]

    view = ListView(items, incomplete_item.project)

    assert incomplete_item in view.incomplete
    assert incomplete_item not in view.complete

    assert complete_item not in view.incomplete
    assert complete_item in view.complete


def test_onetime_and_recurring_are_split() -> None:
    onetime_item = ListItem('test')
    recurring_item = ListItem('test', recurring=True)
    items = [onetime_item, recurring_item]

    view = ListView(items, onetime_item.project)

    assert onetime_item in view.onetime
    assert onetime_item not in view.recurring

    assert recurring_item not in view.onetime
    assert recurring_item in view.recurring


def test_subproject_views_returns_view_of_grouped_items() -> None:
    item2 = ListItem('test2', project=ListItemProject('projectA.produce', ListItemProjectType.checklist))
    item3 = ListItem('test3', project=ListItemProject('projectA.produce', ListItemProjectType.checklist))

    items = [item2, item3]
    view = ListView(items, ListItemProject('projectA', ListItemProjectType.checklist))
    subprojectviews = list(view.subproject_views())
    assert len(subprojectviews) == 1
    assert isinstance(subprojectviews[0], ListView)
    assert subprojectviews[0].project == ListItemProject('projectA.produce', ListItemProjectType.checklist)


def test_subproject_views_groups_only_next_layer() -> None:
    item2 = ListItem('test2', project=ListItemProject('projectA.produce', ListItemProjectType.checklist))
    item3 = ListItem('test3', project=ListItemProject('projectA.produce.fruits', ListItemProjectType.checklist))

    items = [item2, item3]
    view = ListView(items, ListItemProject('projectA', ListItemProjectType.checklist))
    subprojectviews = list(view.subproject_views())
    assert len(subprojectviews) == 1
    assert subprojectviews[0].project == ListItemProject('projectA.produce', ListItemProjectType.checklist)


def test_subproject_views_doesnt_include_group_of_items_of_merely_self() -> None:
    item1 = ListItem('test1', project=ListItemProject('projectA', ListItemProjectType.checklist))
    item2 = ListItem('test2', project=ListItemProject('projectA.produce', ListItemProjectType.checklist))

    items = [item1, item2]
    view = ListView(items, ListItemProject('projectA', ListItemProjectType.checklist))
    subprojectviews = list(view.subproject_views())
    subprojects = [view.project for view in subprojectviews]
    assert ListItemProject('projectA', ListItemProjectType.checklist) not in subprojects


def test_currentproject_view_contains_only_current_project_without_subproject() -> None:
    item1 = ListItem('test1', project=ListItemProject('projectA', ListItemProjectType.checklist))
    item2 = ListItem('test2', project=ListItemProject('projectA.produce', ListItemProjectType.checklist))

    items = [item1, item2]
    view = ListView(items, ListItemProject('projectA', ListItemProjectType.checklist))
    assert view.currentproject.project == ListItemProject('projectA', ListItemProjectType.checklist)
    assert item1 in view.currentproject
    assert item2 not in view.currentproject


# handle when project of original listview is '' and null
#  this would include all items of every project in registry
#  should be grouped by project('', checklist) and project('', todo), etc
# handle when project of original listview is '' but also checklist
#  this is like next level after the above
# should group by root project for a given type ('grocery', checklist) and project('work', checklist)
