import os
import sqlite3
import sys

from uuid6 import UUID

from insync.list import ListItem, ListItemContext, ListItemContextType, ListRegistry

sqlite3.register_adapter(UUID, lambda u: u.bytes_le)
sqlite3.register_converter('UUIDLE', lambda b: UUID(bytes_le=b))

sqlite3.register_adapter(ListItemContextType, lambda c: c.value.to_bytes(1, 'little'))
sqlite3.register_converter('LISTITEMCONTEXTTYPE', lambda b: ListItemContextType(int.from_bytes(b, 'little')))


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
                    context_name TEXT,
                    context_type LISTITEMCONTEXTTYPE,
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
            INSERT INTO list (uuid, description, context_name, context_type, completed)
                VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (uuid)
                DO UPDATE SET
                    description = excluded.description,
                    context_name = excluded.context_name,
                    context_type = excluded.context_type,
                    completed = excluded.completed
            """

        self._conn.executemany(
            sql,
            ((UUID(bytes_le=item.uuid.bytes_le), item.description, item.context.name, item.context.context_type, item.completed) for item in reg.items),
        )

        self._conn.commit()

    def load(self) -> ListRegistry:
        cursor = self._conn.cursor()
        cursor = cursor.execute("""
            SELECT
                uuid,
                description,
                completed,
                context_name,
                context_type
            FROM list
            """)
        reg = ListRegistry()
        for row in cursor:
            print(row[0])
            li = ListItem(
                uuid=row[0],
                description=row[1],
                completed=row[2],
                context=ListItemContext(row[3], row[4]),
            )
            reg.add(li)

        return reg

    def close(self) -> None:
        self._conn.close()
