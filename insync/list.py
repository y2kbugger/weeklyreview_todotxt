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

Priority = Enum('Priority', ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])

class ListItemContextType(Enum):
    NULL = 0
    TODO = 1
    CHECKLIST = 2
    REF = 3


@dataclass
class ListItemContext:
    name: str
    context_type: ListItemContextType

    def __str__(self) -> str:
        if self.context_type == ListItemContextType.TODO:
            prefix = "@"
        elif self.context_type == ListItemContextType.CHECKLIST:
            prefix = "@^"
        elif self.context_type == ListItemContextType.REF:
            prefix = "@#"
        elif self.context_type == ListItemContextType.NULL:
            prefix = ""
        else:
            raise ValueError(f"Unknown context type: {self.context_type}")

        return f'{prefix}{self.name}'

def null_listitemcontext() -> ListItemContext:
    return ListItemContext("", ListItemContextType.NULL)


@dataclass
class ListItem:
    description: str

    uuid: UUID = field(default_factory=uuid7)
    completed: bool = False
    priority: Priority | None = None
    completion_date: dt.date | None = None
    creation_date: dt.date = field(default_factory=dt.date.today)
    context: ListItemContext = field(default_factory=null_listitemcontext)
    # project: Project

    def __str__(self) -> str:
        # x (A) 2016-05-20 2016-04-30 measure space for +chapelShelving @chapel due:2016-05-30
        pieces = [
            "x" if self.completed else "",
            f"({self.priority.value})" if self.priority else "",
            str(self.completion_date) if self.completion_date else "",
            str(self.creation_date),
            self.description,
            str(self.context) if self.context else "",
        ]
        return ' '.join(p for p in pieces if p != '')

@dataclass
class ListRegistry:
    _list: dict[UUID, ListItem] = field(default_factory=dict)
    _history: list[Command] = field(default_factory=list)

    def __str__(self) -> str:
        return '\n'.join(str(item) for item in self._list.values()) + '\n'

    @property
    def items(self) -> Iterable[ListItem]:
        return sorted(self._list.values(), key=lambda item: (item.completed, item.description.lower()))

    def add(self, item: ListItem) -> None:
        self._list[item.uuid] = item

    def do(self, command: Command) -> None:
        item = self._list[command.uuid]
        command.do(item)
        self._history.append(command)

    @property
    def undo_stack(self) -> Iterable[Command]:
        yield from reversed(self._history)

    def _undo(self, command: Command) -> None:
        item = self._list[command.uuid]
        command.undo(item)
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

    uuid: UUID

    def do(self, item: ListItem) -> None:
        raise NotImplementedError

    def undo(self, item: ListItem) -> None:
        raise NotImplementedError

class ImpotentCommandError(Exception):
    def __init__(self, command: Command):
        super().__init__(f"Command {command} is impotent")

@dataclass
class CompletionCommand(Command):
    completed_new: bool
    completed_orig: bool | None = None

    def __init__(self, uuid: UUID, completed: bool):
        self.uuid = uuid
        self.completed_new = completed

    def do(self, item: ListItem) -> None:
        if self.completed_new == item.completed:
            raise ImpotentCommandError(self)
        self.completed_orig = item.completed
        item.completed = self.completed_new

    def undo(self, item: ListItem) -> None:
        assert self.completed_orig is not None, "Undoing a command that has not been done"
        item.completed = self.completed_orig

