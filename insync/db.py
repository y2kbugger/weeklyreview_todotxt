import sqlite3

from insync.list import ListRegistry

class ListDB:
    def __init__(self, db_path: str):
        self.db_path = db_path or ':memory:'
        self.conn = sqlite3.connect(db_path)
        try:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS list (
                    id TEXT PRIMARY KEY,
                    description TEXT,
                    context TEXT,
                    completed INTEGER
                    )
                """
            )
        except sqlite3.OperationalError:
            # table already exists
            pass
        self.conn.commit()
        self.conn.close()

    def patch(self, reg: ListRegistry):
        self.conn = sqlite3.connect(self.db_path)
        sql = """
            INSERT INTO list (id, description, context, completed)
            VALUES (?, ?, ?, ?)
            """
        # can you do this in a single statement?
        self.conn.executemany(
            sql,
            ((str(item.id), item.description, str(item.context), item.completed) for item in reg._list.values())
            )

        self.conn.commit()
        self.conn.close()