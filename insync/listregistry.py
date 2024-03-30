from __future__ import annotations

import datetime as dt
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum

from uuid6 import UUID, uuid7

"""
- map our concepts to todo.txt
  - completed `x`
  - priorty `(A) `
  - completion-date `2020-01-01`
  - creation-date `2020-01-01`
  - context `@home` `@car`
  - project: `+house`
  - simpletask extensions
    - due-date `due:2020-01-01`
    - threshold `t:2024-12-31`
    - hidden `h:1`
  - our extensions
    - completion_datetime `2020-01-01T21:39:27-05:00`
    - creation_datetime `2020-01-01T21:39:27-05:00`
    - archival_datetime `archived:2020-01-01T21:39:27-05:00`
    - project-tree `+house.garage`
      - and we only allow one per item
      - type prefixs
        - `+` - todo
        - `+^` - checklist
        - `+#` - reference
    - cost `$:100`
    - effort `hours:2.5`
    - recurable `rec:true`
      - could have recurrance rules, true is manual which is the only one we support for now
"""

ListItemPriority = Enum(
    'Priority',
    ((p, p) for p in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']),
    type=str,
)


class ListItemProjectType(str, Enum):
    null = "null"
    todo = "todo"
    checklist = "checklist"
    ref = "ref"


@dataclass(frozen=True)
class ListItemProject:
    name: str
    project_type: ListItemProjectType

    def __str__(self) -> str:
        if self.project_type == ListItemProjectType.todo:
            prefix = "+"
        elif self.project_type == ListItemProjectType.checklist:
            prefix = "+^"
        elif self.project_type == ListItemProjectType.ref:
            prefix = "+#"
        elif self.project_type == ListItemProjectType.null:
            prefix = ""
        else:
            raise ValueError(f"Unknown project type: {self.project_type}")

        return f'{prefix}{self.name}'

    @property
    def name_parts(self) -> list[str]:
        if len(self.name) == 0:
            return []
        else:
            return self.name.split('.')

    def __contains__(self, other: ListItemProject) -> bool:
        # null acts as a wildcard
        if self.project_type != ListItemProjectType.null and self.project_type != other.project_type:
            return False

        # project cannot contain a project which is more general
        # e.g grocery.produce does not include all grocery, (but grocery does include grocery.produce)
        if len(self.name_parts) > len(other.name_parts):
            return False

        return all(a == b for a, b in zip(self.name_parts, other.name_parts))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ListItemProject):
            return False
        return self.name == other.name and self.project_type == other.project_type


class NullListItemProject(ListItemProject):
    def __init__(self):
        super().__init__("", ListItemProjectType.null)


@dataclass
class ListItem:
    description: str

    @property
    def completed(self) -> bool:
        return self.completion_datetime is not None

    @property
    def archived(self) -> bool:
        return self.archival_datetime is not None

    uuid: UUID = field(default_factory=uuid7)
    priority: ListItemPriority | None = None
    completion_datetime: dt.datetime | None = None
    creation_datetime: dt.datetime = field(default_factory=lambda: dt.datetime.now(tz=dt.timezone.utc))
    archival_datetime: dt.datetime | None = None
    project: ListItemProject = field(default_factory=NullListItemProject)

    def __str__(self) -> str:
        # x (A) 2016-05-20 2016-04-30 measure space for +chapelShelving @chapel due:2016-05-30
        # TODO: add archived and recurring flags to the string representation (and in todo.txt web page)
        pieces = [
            "x" if self.completed else "",
            f"({self.priority.value})" if self.priority else "",
            str(self.completion_datetime) if self.completion_datetime else "",
            str(self.creation_datetime),
            self.description,
            str(self.project) if self.project else "",
        ]
        return ' '.join(p for p in pieces if p != '')


@dataclass
class ListRegistry:
    _list: dict[UUID, ListItem] = field(default_factory=dict)
    _history: list[Command] = field(default_factory=list)

    def __str__(self) -> str:
        return '\n'.join(str(item) for item in self._list.values()) + '\n'

    @property
    def all_items(self) -> Iterable[ListItem]:
        """Return all items, including archived ones."""
        return sorted(self._list.values(), key=lambda item: (item.completed, item.description.lower()))

    @property
    def items(self) -> Iterable[ListItem]:
        _items = filter(lambda item: not item.archived, self.all_items)
        return _items

    def get_item(self, uuid: UUID) -> ListItem:
        return self._list[uuid]

    def add(self, item: ListItem) -> None:
        self._list[item.uuid] = item

    def remove(self, uuid: UUID) -> None:
        self._list.pop(uuid)

    def do(self, command: Command) -> None:
        command.do(self)
        self._history.append(command)

    @property
    def undo_stack(self) -> Iterable[Command]:
        yield from reversed(self._history)

    def _undo(self, command: Command) -> None:
        command.undo(self)
        self._history.remove(command)

    def undo(self, command: Command | None = None) -> None:
        """Undo specific command or else the most recent command in the history."""
        self._undo(command or self._history[-1])


@dataclass
class Command:
    """Command to do and undo a mutation to the list

    - It must be initialized with all the information it needs to do its job.
    - It can collect the info it needs to undo while doing its job.
    - It is not legal to undo a command that has not been done.
    """

    done: bool

    def do(self, reg: ListRegistry) -> None:
        raise NotImplementedError

    def undo(self, reg: ListRegistry) -> None:
        raise NotImplementedError


@dataclass
class CreateCommand(Command):
    uuid: UUID
    item: ListItem

    def __init__(self, uuid: UUID, item: ListItem):
        self.done = False
        self.uuid = uuid
        self.item = item

    def do(self, reg: ListRegistry) -> None:
        assert not self.done, "Attempting to do a CreateCommand that has already been done"
        reg.add(self.item)
        self.done = True

    def undo(self, reg: ListRegistry) -> None:
        assert self.done, "Attempting to undo do a CreateCommand that has not been done"
        reg.remove(self.uuid)
        self.done = False


@dataclass
class CompletionCommand(Command):
    uuid: UUID
    completion_datetime_new: dt.datetime | None
    completion_datetime_orig: dt.datetime | None

    def __init__(self, uuid: UUID, completed: bool):
        self.done = False
        self.uuid = uuid
        self.completion_datetime_new = dt.datetime.now(tz=dt.timezone.utc) if completed else None

    def do(self, reg: ListRegistry) -> None:
        assert not self.done, "Attempting to do a CompletionCommand that has already been done"
        item = reg.get_item(self.uuid)
        self.completion_datetime_orig = item.completion_datetime
        item.completion_datetime = self.completion_datetime_new
        self.done = True

    def undo(self, reg: ListRegistry) -> None:
        assert self.done, "Attempting to undo a CompletionCommand that has not been done"
        item = reg.get_item(self.uuid)
        item.completion_datetime = self.completion_datetime_orig
        self.done = False


@dataclass
class ArchiveCommand(Command):
    uuid: UUID
    archival_datetime_new: dt.datetime | None
    archival_datetime_orig: dt.datetime | None = None

    def __init__(self, uuid: UUID, archived: bool):
        self.done = False
        self.uuid = uuid
        self.archival_datetime_new = dt.datetime.now(tz=dt.timezone.utc) if archived else None

    def do(self, reg: ListRegistry) -> None:
        assert not self.done, "Attempting to do a ArchiveCommand that has already been done"
        item = reg.get_item(self.uuid)
        self.archival_datetime_orig = item.archival_datetime
        item.archival_datetime = self.archival_datetime_new
        self.done = True

    def undo(self, reg: ListRegistry) -> None:
        assert self.done, "Attempting to undo a ArchiveCommand that has not been done"
        item = reg.get_item(self.uuid)
        item.archival_datetime = self.archival_datetime_orig
        self.done = False


@dataclass
class ChecklistResetCommand(Command):
    archived: list[UUID]
    project: ListItemProject

    def __init__(self, project: ListItemProject):
        self.done = False
        assert project.project_type == ListItemProjectType.checklist, "ResetChecklistCommand only works with checklists"
        self.archival_datetime = dt.datetime.now(tz=dt.timezone.utc)
        self.archived = []
        self.project = project

    def do(self, reg: ListRegistry) -> None:
        assert not self.done, "Attempting to do a ChecklistResetCommand that has already been done"
        for item in reg.items:
            if item.completed and item.project == self.project:
                # archive completed items
                item.archival_datetime = self.archival_datetime
                self.archived.append(item.uuid)
                # TODO: make recurring items recur
        self.done = True

    def undo(self, reg: ListRegistry) -> None:
        assert self.done, "Attempting to undo a ChecklistResetCommand that has not been done"
        for uuid in self.archived:
            reg.get_item(uuid).archival_datetime = None
        self.done = False
