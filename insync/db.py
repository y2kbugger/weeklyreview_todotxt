import datetime as dt
import os
import sqlite3
import sys
from enum import Enum

from uuid6 import UUID

from insync.listitem import ListItem, ListItemProject, ListItemProjectType
from insync.listregistry import ListRegistry


def adapt_datetime(dtval: dt.datetime) -> str:
    assert dtval.tzinfo is not None, "Datetime must have timezone info"
    return dtval.isoformat("T")


def convert_timestamp(ts: bytes) -> dt.datetime:
    dtval = dt.datetime.fromisoformat(ts.decode())
    assert dtval.tzinfo is not None, "Datetime must have timezone info"
    return dtval


sqlite3.register_adapter(dt.datetime, adapt_datetime)
sqlite3.register_converter("TIMESTAMP", convert_timestamp)

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
                    creation_datetime TIMESTAMP,
                    description TEXT,
                    project_name TEXT,
                    project_type LISTITEMPROJECTTYPE,
                    completion_datetime TIMESTAMP,
                    archival_datetime TIMESTAMP,
                    priority TEXT,
                    recurring BOOLEAN
                    )
                """,
            )
        except sqlite3.OperationalError:
            print("Table already exists", file=sys.stderr)

        self._conn.commit()

    def patch(self, reg: ListRegistry) -> None:
        # TODO: Track mutations and only upsert those

        sql = """
            INSERT INTO list (
                uuid,
                creation_datetime,
                description,
                project_name,
                project_type,
                completion_datetime,
                archival_datetime,
                priority,
                recurring
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (uuid)
                DO UPDATE SET
                    creation_datetime = excluded.creation_datetime,
                    description = excluded.description,
                    project_name = excluded.project_name,
                    project_type = excluded.project_type,
                    completion_datetime = excluded.completion_datetime,
                    archival_datetime = excluded.archival_datetime,
                    priority = excluded.priority,
                    recurring = excluded.recurring
            """

        self._conn.executemany(
            sql,
            (
                (
                    item.uuid.bytes_le,
                    item.creation_datetime,
                    item.description,
                    item.project.name,
                    item.project.project_type,
                    item.completion_datetime,
                    item.archival_datetime,
                    item.priority,
                    item.recurring,
                )
                for item in reg
            ),
        )

        self._conn.commit()

    def load(self) -> ListRegistry:
        cursor = self._conn.cursor()
        cursor = cursor.execute("""
            SELECT
                uuid,
                description,
                completion_datetime,
                project_name,
                project_type,
                archival_datetime,
                creation_datetime,
                priority,
                recurring
            FROM list
            """)
        reg = ListRegistry()
        for row in cursor:
            li = ListItem(
                uuid=row[0],
                creation_datetime=row[6],
                description=row[1],
                completion_datetime=row[2],
                archival_datetime=row[5],
                project=ListItemProject(row[3], row[4]),
                priority=row[7],
                recurring=row[8],
            )
            reg.add(li)

        return reg

    def close(self) -> None:
        self._conn.close()
