import sqlite3
import sys

from insync.list import ListItem, ListRegistry


class ListDB:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)

    def ensure_tables_created(self) -> None:
        try:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS list (
                    uuid TEXT PRIMARY KEY,
                    description TEXT,
                    context TEXT,
                    completed INTEGER
                    )
                """,
            )
        except sqlite3.OperationalError:
            print("Table already exists", file=sys.stderr)

        self.conn.commit()

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

        self.conn.executemany(
            sql,
            ((str(item.uuid), item.description, str(item.context), item.completed) for item in reg._list.values()),
        )

        self.conn.commit()

    def load(self) -> ListRegistry:
        cursor = self.conn.execute("""
            SELECT
                uuid,
                description,
                completed,
                context
            FROM list
            """)
        reg = ListRegistry()
        for row in cursor:
            li = ListItem(
                uuid=row[0],
                description=row[1],
                completed=row[2],
                context=row[3], #TODO: this is totally the wrong type but looks correct in the the scratch.py
            )
            reg.add(li)

        return reg

    def close(self) -> None:
        self.conn.close()
