"""This module contains the database code to store data in a local file using
the SQLite3 database engine."""
import sqlite3
from pathlib import Path
from typing import List, Union


class Database:
    """This class represents the SQLite database."""

    def __init__(
        self,
        db_file: Union[Path, str] = ":memory:",
        initial_sql_script: Path = None,
    ):
        """Initialize the database."""
        if initial_sql_script:
            if isinstance(initial_sql_script, Path):
                self.initial_sql_script = initial_sql_script
            elif isinstance(initial_sql_script, str):
                self.initial_sql_script = Path(initial_sql_script)
            else:
                raise TypeError(
                    (
                        f"initial_sql_script must be a Path or str."
                        f"Not {type(initial_sql_script)}"
                    )
                )

            self.initial_sql_script.parent.mkdir(parents=True, exist_ok=True)
            with open(
                self.initial_sql_script, "r", encoding="utf-8"
            ) as sql_script:
                sql = sql_script.read()
                self.conn = sqlite3.connect(db_file)
                self.conn.executescript(sql)
                self.conn.commit()
        else:
            raise TypeError(
                "initial_sql_script must be a Path or str. not None"
            )

        if isinstance(db_file, str):
            if db_file == ":memory:":
                self.db_file = db_file
            else:
                self.db_file = Path(db_file)
        elif isinstance(db_file, Path):
            self.db_file = db_file
            self.db_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            raise TypeError("db_file must be a Path or str")

        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def create_table(self, table_name: str, columns: List[str]):
        """Create a table in the database."""
        columns = ", ".join(columns)
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        self.cursor.execute(sql)
        self.conn.commit()

    def insert(self, table_name: str, columns: List[str], values: List[str]):
        """Insert a row into the database."""
        columns = ", ".join(columns)
        values_placeholders = ", ".join(["?" for _ in range(len(values))])
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values_placeholders})"
        self.cursor.execute(sql, values)
        self.conn.commit()

    def select(self, table_name: str, columns: List[str], where: str = None):
        """Select rows from the database."""
        columns = ", ".join(columns)
        sql = f"SELECT {columns} FROM {table_name}"
        if where:
            sql += f" WHERE {where}"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def update(
        self,
        table_name: str,
        columns: List[str],
        values: List[str],
        where: str = None,
    ):
        """Update rows in the database."""
        columns = ", ".join([f"{col} = ?" for col in columns])
        sql = f"UPDATE {table_name} SET {columns}"
        if where:
            sql += f" WHERE {where}"
        self.cursor.execute(sql, values)
        self.conn.commit()

    def delete(self, table_name: str, where: str = None):
        """Delete rows from the database."""
        sql = f"DELETE FROM {table_name}"
        if where:
            sql += f" WHERE {where}"
        self.cursor.execute(sql)
        self.conn.commit()

    def close(self):
        """Close the database."""
        self.conn.close()

    def get_columns(self, table_name: str) -> List[str]:
        """Return a list of columns in the table."""
        sql = f"PRAGMA table_info({table_name});"
        self.cursor.execute(sql)
        columns = self.cursor.fetchall()
        result = [column["name"] for column in columns]
        return result

    def get_tables(self) -> List[str]:
        """Return a list of tables in the database."""
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = self.cursor.fetchall()
        self.conn.close()

        # This list comprehension is used to convert the list of tuples
        # returned to a list of strings.
        result = [table[0] for table in tables if table != "sqlite_sequence"]
        return result
    
    def table_exists(self, table_name: str) -> bool:
        """Return True if the table exists in the database."""
        tables = self.get_tables()
        return table_name in tables
