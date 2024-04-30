from __future__ import annotations

import datetime as dt
from collections.abc import Iterator
from dataclasses import dataclass, field

from uuid6 import UUID

from insync.listitem import ListItem, ListItemProject, ListItemProjectType
from insync.listview import ListView


@dataclass
class ListRegistry:
    _items: dict[UUID, ListItem] = field(default_factory=dict)

    def __str__(self) -> str:
        return '\n'.join(str(item) for item in self._items.values()) + '\n'

    def __contains__(self, item: ListItem) -> bool:
        return item.uuid in self._items

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[ListItem]:
        return iter(self._items.values())

    def get_item(self, uuid: UUID) -> ListItem:
        return self._items[uuid]

    def add(self, item: ListItem) -> None:
        self._items[item.uuid] = item

    def remove(self, uuid: UUID) -> None:
        self._items.pop(uuid)

    ### ListView Creation ###
    def search(self, project: ListItemProject) -> ListView:
        items = filter(lambda item: item.project in project, self._items.values())
        return ListView(items, project)

    ### Do/Undo/Redo ###
    _undostack: list[Command] = field(default_factory=list)
    _redostack: list[Command] = field(default_factory=list)

    def do(self, command: Command) -> None:
        command.do(self)
        self._undostack.append(command)

    def undo(self) -> None:
        command = self._undostack.pop()
        command.undo(self)
        self._redostack.append(command)

    def redo(self) -> None:
        self.do(self._redostack.pop())


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
class RecurringCommand(Command):
    uuid: UUID
    recurring_new: bool
    recurring_orig: bool

    def __init__(self, uuid: UUID, recurring: bool):
        self.done = False
        self.uuid = uuid
        self.recurring_new = recurring

    def do(self, reg: ListRegistry) -> None:
        assert not self.done, "Attempting to do a RecurringCommand that has already been done"
        item = reg.get_item(self.uuid)
        self.recurring_orig = item.recurring
        item.recurring = self.recurring_new
        self.done = True

    def undo(self, reg: ListRegistry) -> None:
        assert self.done, "Attempting to undo a RecurringCommand that has not been done"
        item = reg.get_item(self.uuid)
        item.recurring = self.recurring_orig
        self.done = False


@dataclass
class ChecklistResetCommand(Command):
    archived: list[UUID]
    project: ListItemProject

    @dataclass
    class _PreRecurState:
        uuid: UUID
        completion_datetime: dt.datetime

    def __init__(self, project: ListItemProject):
        self.done = False
        assert project.project_type == ListItemProjectType.checklist, "ResetChecklistCommand only works with checklists"
        self.checklist_reset_datetime = dt.datetime.now(tz=dt.timezone.utc)
        self.archived = []

        self.recurred = []
        self.project = project

    def do(self, reg: ListRegistry) -> None:
        assert not self.done, "Attempting to do a ChecklistResetCommand that has already been done"
        for item in reg:
            if item.project not in self.project:
                continue

            if item.completion_datetime is None:
                # not completed, so skip
                continue

            if item.recurring:
                # recur the item
                prs = self._PreRecurState(item.uuid, item.completion_datetime)
                item.completion_datetime = None
                self.recurred.append(prs)
            else:
                # archive the item
                item.archival_datetime = self.checklist_reset_datetime
                self.archived.append(item.uuid)

        self.done = True

    def undo(self, reg: ListRegistry) -> None:
        assert self.done, "Attempting to undo a ChecklistResetCommand that has not been done"
        for uuid in self.archived:
            reg.get_item(uuid).archival_datetime = None
        for prs in self.recurred:
            reg.get_item(prs.uuid).completion_datetime = prs.completion_datetime
        self.done = False
