import os
import sqlite3
import sys
from enum import Enum

from uuid6 import UUID

from insync.listregistry import ListItem, ListItemProject, ListItemProjectType, ListRegistry

sqlite3.register_adapter(UUID, lambda u: u.bytes_le)
sqlite3.register_converter('UUIDLE', lambda b: UUID(bytes_le=b))


class _ListItemProjectTypeInt(Enum):
    """Encode ListItemProjectType as an integer for storage in SQLite."""

    null = 0
    todo = 1
    checklist = 2
    ref = 3


sqlite3.register_adapter(ListItemProjectType, lambda c: _ListItemProjectTypeInt[c.value].value.to_bytes(1, 'little'))
sqlite3.register_converter('LISTITEMPROJECTTYPE', lambda b: ListItemProjectType(_ListItemProjectTypeInt(int.from_bytes(b, 'little')).name))


class ListDB:

    def __init__(self, db_path: str | os.PathLike):
        self._conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)

    def ensure_tables_created(self) -> None:
        try:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS list (
                    uuid UUIDLE PRIMARY KEY,
                    description TEXT,
                    project_name TEXT,
                    project_type LISTITEMPROJECTTYPE,
                    completed INTEGER
                    )
                """,
            )
        except sqlite3.OperationalError:
            print("Table already exists", file=sys.stderr)

        self._conn.commit()

    def patch(self, reg: ListRegistry) -> None:
        # TODO: Track mutations and only upsert those

        sql = """
            INSERT INTO list (uuid, description, project_name, project_type, completed)
                VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (uuid)
                DO UPDATE SET
                    description = excluded.description,
                    project_name = excluded.project_name,
                    project_type = excluded.project_type,
                    completed = excluded.completed
            """

        self._conn.executemany(
            sql,
            ((UUID(bytes_le=item.uuid.bytes_le), item.description, item.project.name, item.project.project_type, item.completed) for item in reg.items),
        )

        self._conn.commit()

    def load(self) -> ListRegistry:
        cursor = self._conn.cursor()
        cursor = cursor.execute("""
            SELECT
                uuid,
                description,
                completed,
                project_name,
                project_type
            FROM list
            """)
        reg = ListRegistry()
        for row in cursor:
            print(row[0])
            li = ListItem(
                uuid=row[0],
                description=row[1],
                completed=row[2],
                project=ListItemProject(row[3], row[4]),
            )
            reg.add(li)

        return reg

    def close(self) -> None:
        self._conn.close()
