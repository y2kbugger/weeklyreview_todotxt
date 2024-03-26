from __future__ import annotations

import datetime as dt
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum

from uuid6 import UUID, uuid7

"""
- map our concepts to todo.txt
  - priorty `(A) `
  - context `@home` `@car`
  - project: `+house`
  - simpletask extensions
    - due-date `due:2020-01-01`
    - threshold `t:2024-12-31`
  - our extensions
    - project-tree `+house.garage`
    - cost `$:100`
    - effort `hours:2.5`
    - type `type:[checklist|todo|ref|checklist.onetime]`
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

    uuid: UUID = field(default_factory=uuid7)
    completed: bool = False
    archived: bool = False
    priority: ListItemPriority | None = None
    completion_date: dt.date | None = None
    creation_date: dt.date = field(default_factory=dt.date.today)
    project: ListItemProject = field(default_factory=NullListItemProject)

    def __str__(self) -> str:
        # x (A) 2016-05-20 2016-04-30 measure space for +chapelShelving @chapel due:2016-05-30
        # TODO: add archived and recurring flags to the string representation (and in todo.txt web page)
        pieces = [
            "x" if self.completed else "",
            f"({self.priority.value})" if self.priority else "",
            str(self.completion_date) if self.completion_date else "",
            str(self.creation_date),
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

    def do(self, reg: ListRegistry) -> None:
        raise NotImplementedError

    def undo(self, reg: ListRegistry) -> None:
        raise NotImplementedError


@dataclass
class CreateCommand(Command):
    uuid: UUID
    item: ListItem

    def __init__(self, uuid: UUID, item: ListItem):
        self.uuid = uuid
        self.item = item

    def do(self, reg: ListRegistry) -> None:
        reg.add(self.item)

    def undo(self, reg: ListRegistry) -> None:
        reg.remove(self.uuid)


@dataclass
class CompletionCommand(Command):
    uuid: UUID
    completed_new: bool
    completed_orig: bool | None = None

    def __init__(self, uuid: UUID, completed: bool):
        self.uuid = uuid
        self.completed_new = completed

    def do(self, reg: ListRegistry) -> None:
        item = reg.get_item(self.uuid)
        self.completed_orig = item.completed
        item.completed = self.completed_new

    def undo(self, reg: ListRegistry) -> None:
        item = reg.get_item(self.uuid)
        assert self.completed_orig is not None, "Undoing a CompletionCommand that has not been done"
        item.completed = self.completed_orig

@dataclass
class ArchiveCommand(Command):
    uuid: UUID
    archived_new: bool
    archived_orig: bool | None = None

    def __init__(self, uuid: UUID, archived: bool):
        self.uuid = uuid
        self.archived_new = archived

    def do(self, reg: ListRegistry) -> None:
        item = reg.get_item(self.uuid)
        self.archived_orig = item.archived
        item.archived = self.archived_new

    def undo(self, reg: ListRegistry) -> None:
        item = reg.get_item(self.uuid)
        assert self.archived_orig is not None, "Undoing a ArchiveCommand that has not been done"
        item.archived = self.archived_orig

@dataclass
class ChecklistResetCommand(Command):
    archived: list[UUID]
    project: ListItemProject

    def __init__(self, project: ListItemProject):
        assert project.project_type == ListItemProjectType.checklist, "ResetChecklistCommand only works with checklists"
        self.archived = []
        self.project = project

    def do(self, reg: ListRegistry) -> None:
        for item in reg.items:
            if item.completed and item.project == self.project:
                # archive completed items
                item.archived = True
                self.archived.append(item.uuid)
                # TODO: make recurring items recur

    def undo(self, reg: ListRegistry) -> None:
        for uuid in self.archived:
            reg.get_item(uuid).archived = False
