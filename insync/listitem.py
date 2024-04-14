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

    def __len__(self) -> int:
        return len(self.name_parts)

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

    def truncate(self, num_parts: int) -> ListItemProject:
        return ListItemProject('.'.join(self.name_parts[:num_parts]), self.project_type)

    @classmethod
    def common_root(cls, projects: Iterable[ListItemProject]) -> ListItemProject:
        ps = list(projects)
        if not len(ps):
            return NullListItemProject()

        if len({p.project_type for p in ps}) > 1:
            # multiple project types, return the null project
            return NullListItemProject()
        else:
            project_type = ps[0].project_type

        project_partss = [p.name_parts for p in ps]

        # Initialize the shortest tuple to compare to others (optimization step)
        shortest = min(project_partss, key=len)

        # Iterate over each index and element in the shortest tuple
        for i, value in enumerate(shortest):
            for t in project_partss:
                # If mismatch is found, return the current longest prefix
                if t[i] != value:
                    return ListItemProject('.'.join(shortest[:i]), project_type)

        # If no mismatch, return the entire shortest tuple
        return ListItemProject('.'.join(shortest), project_type)


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
    recurring: bool = False

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
            f"archived:{self.archival_datetime}" if self.archival_datetime else "",
            "rec:true" if self.recurring else "",
        ]
        return ' '.join(p for p in pieces if p != '')
