"""This module contains the database code to store data in a local file using
the SQLite3 database engine."""
import sqlite3
from pathlib import Path
from typing import List, Union


class Database:
    """This class represents the SQLite database."""

    def __init__(self, db_file: Union[Path, str] = ":memory:"):
        """Initialize the database."""
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
