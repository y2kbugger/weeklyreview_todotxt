from collections.abc import Iterable, Iterator

from insync.listitem import ListItem


class ListView:
    def __init__(self, items: Iterable[ListItem]):
        self._items = list(items)

    def __iter__(self) -> Iterator[ListItem]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, item: ListItem) -> bool:
        return item in self._items

    @property
    def active_items(self) -> Iterable[ListItem]:
        return filter(lambda item: not item.archived, self)

    @property
    def archived_items(self) -> Iterable[ListItem]:
        return filter(lambda item: item.archived, self)
