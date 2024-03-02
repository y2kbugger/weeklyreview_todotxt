import os
import sqlite3
import sys

from uuid6 import UUID

from insync.list import ListItem, ListRegistry

sqlite3.register_adapter(UUID, lambda u: u.bytes_le)
sqlite3.register_converter('UUIDLE', lambda b: UUID(bytes_le=b))


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
                    context TEXT,
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
            INSERT INTO list (uuid, description, context, completed)
                VALUES (?, ?, ?, ?)
            ON CONFLICT (uuid)
                DO UPDATE SET
                    description = excluded.description,
                    context = excluded.context,
                    completed = excluded.completed
            """

        self._conn.executemany(
            sql,
            ((UUID(bytes_le=item.uuid.bytes_le), item.description, item.context, item.completed) for item in reg.items),
        )

        self._conn.commit()

    def load(self) -> ListRegistry:
        cursor = self._conn.cursor()
        cursor = cursor.execute("""
            SELECT
                uuid,
                description,
                completed,
                context
            FROM list
            """)
        reg = ListRegistry()
        for row in cursor:
            print(row[0])
            li = ListItem(
                uuid=row[0],
                description=row[1],
                completed=row[2],
                context=row[3],  # TODO: this is totally the wrong type but looks correct in the the scratch.py
            )
            reg.add(li)

        return reg

    def close(self) -> None:
        self._conn.close()
