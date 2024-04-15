from __future__ import annotations

from collections.abc import Iterable, Iterator

from insync.listitem import ListItem, ListItemProject


class ListView:
    def __init__(self, items: Iterable[ListItem], project: ListItemProject):
        self._items = list(items)
        common_root_project = ListItemProject.common_root(item.project for item in self)
        if len(common_root_project) > 0:
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
    def incomplete(self) -> ListView:
        return ListView((i for i in self if not i.completed), self.project)

    @property
    def complete(self) -> ListView:
        return ListView((i for i in self if i.completed), self.project)

    @property
    def active(self) -> ListView:
        return ListView((i for i in self if not i.archived), self.project)

    @property
    def archived(self) -> ListView:
        return ListView((i for i in self if i.archived), self.project)

    @property
    def onetime(self) -> ListView:
        return ListView((i for i in self if not i.recurring), self.project)

    @property
    def recurring(self) -> ListView:
        return ListView((i for i in self if i.recurring), self.project)

    @property
    def currentproject(self) -> ListView:
        """Return a view containing only items of the current project."""
        return ListView((i for i in self if i.project == self.project), self.project)

    def subproject_views(self) -> Iterable[ListView]:
        """Return a list of subviews, each containing items of a subproject.

        e.g given that the current project is 'grocery', and there are items with projects:
         - 'grocery'
         - 'grocery.produce'
         - 'grocery.produce.fruits'
         - 'grocery.dairy'

         only two subviews will be returned:
         - 'grocery.produce' includes items with projects 'grocery.produce' and 'grocery.produce.fruits'
         - 'grocery.dairy'
        """
        subprojects = {item.project.truncate(len(self.project) + 1) for item in self}
        if self.project in subprojects:
            subprojects.remove(self.project)
        for subproject in subprojects:
            subproject_items = filter(lambda item: item.project in subproject, self)
            yield ListView(subproject_items, subproject)
