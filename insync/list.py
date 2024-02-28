from __future__ import annotations
from dataclasses import dataclass, field
import datetime as dt
from enum import Enum
from uuid6 import uuid7, UUID
from typing import List, Dict

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

class ContextType(Enum):
    TODO = 0
    CHECKLIST = 1
    REF = 2

class Context:
    def __init__(self, name: str, context_type: ContextType):
        self.name = name
        self.context_type = context_type

    def __str__(self) -> str:
        if self.context_type == ContextType.TODO:
            prefix = "@"
        elif self.context_type == ContextType.CHECKLIST:
            prefix = "@^"
        elif self.context_type == ContextType.REF:
            prefix = "@#"
        else:
            raise ValueError(f"Unknown context type: {self.context_type}")

        return f'{prefix}{self.name}'

@dataclass
class ListItem:
    description: str

    id: UUID = field(default_factory=uuid7)
    completed: bool = False
    priority: Priority | None = None
    completion_date: dt.date | None = None
    creation_date: dt.date = field(default_factory=dt.date.today)
    context: Context | None = None
    # project: Project

    def __str__(self) -> str:
        # x (A) 2016-05-20 2016-04-30 measure space for +chapelShelving @chapel due:2016-05-30
        pieces = [
            'x' if self.completed else '',
            f'({self.priority.value})' if self.priority else '',
            str(self.completion_date) if self.completion_date else '',
            str(self.creation_date),
            self.description,
            str(self.context) if self.context else ''
            ]
        return ' '.join(p for p in pieces if p != '')

@dataclass
class ListRegistry:
    _list: Dict[UUID,ListItem] = field(default_factory=dict)
    _history: List[Command] = field(default_factory=list)

    def __str__(self) -> str:
        return '\n'.join(str(item) for item in self._list.values()) + '\n'

    def add(self, item: ListItem):
        self._list[item.id] = item

    def do(self, command: Command):
        item = self._list[command.id]
        command.do(item)
        self._history.append(command)

    def undo(self, command: Command):
        item = self._list[command.id]
        command.undo(item)
        self._history.remove(command)


@dataclass
class Command():
    """Command to do and undo a mutation to the list

    - It must be initialized with all the information it needs to do its job.
    - It can collect the info it needs to undo while doing its job.
    - It is not legal to undo a command that has not been done.
    """
    id: UUID
    def do(self, item: ListItem) -> ListItem:
        raise NotImplementedError

    def undo(self, item: ListItem) -> ListItem:
        raise NotImplementedError

class ImpotentCommandError(Exception):
    def __init__(self, command: Command):
        super().__init__(f"Command {command} is impotent")

@dataclass
class CompletionCommand(Command):
    completed_new: bool
    completed_orig: bool | None = None
    def __init__(self, id: UUID, completed: bool):
        self.id = id
        self.completed_new = completed

    def do(self, item: ListItem):
        if self.completed_new == item.completed:
            raise ImpotentCommandError(self)
        self.completed_orig = item.completed
        item.completed = self.completed_new

    def undo(self, item: ListItem):
        assert self.completed_orig is not None, "Undoing a command that has not been done"
        item.completed = self.completed_orig

