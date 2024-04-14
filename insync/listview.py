from __future__ import annotations

from collections.abc import Iterable, Iterator

from insync.listitem import ListItem, ListItemProject


class ListView:
    def __init__(self, items: Iterable[ListItem], project: ListItemProject):
        self._items = list(items)
        common_root_project = ListItemProject.common_root(item.project for item in self)
        assert common_root_project in project
        self._project = project

    def __iter__(self) -> Iterator[ListItem]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, item: ListItem) -> bool:
        return item in self._items

    @property
    def project(self) -> ListItemProject:
        return self._project

    @property
    def active_items(self) -> Iterable[ListItem]:
        return filter(lambda item: not item.archived, self)

    @property
    def archived_items(self) -> Iterable[ListItem]:
        return filter(lambda item: item.archived, self)

    def group_by_subproject(self) -> Iterable[ListView]:
        """Return a list of subviews, each containing items of a subproject.
        if there are items that are not sorted into a subproject, they will be included in first group, which is just the current project, but excluding descendants.

        e.g given that the current project is 'grocery', and there are items with projects:
         - 'grocery'
         - 'grocery.produce'
         - 'grocery.produce.fruits'
         - 'grocery.dairy'
         three subviews will be returned:
         - 'grocery'
         - 'grocery.produce'
         - 'grocery.dairy'
        """
        subprojects = {item.project.truncate(len(self.project) + 1) for item in self}
        if self.project in subprojects:
            subprojects.remove(self.project)
            subproject_items = filter(lambda item: item.project == self.project, self)
            yield ListView(subproject_items, self.project)
        for subproject in subprojects:
            subproject_items = filter(lambda item: item.project in subproject, self)
            yield ListView(subproject_items, subproject)
