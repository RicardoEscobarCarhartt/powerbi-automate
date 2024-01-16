"""This module creates a logger for the application."""
import logging
from pathlib import Path
from typing import Union

from carhartt_pbi_automate.database import Database
from carhartt_pbi_automate.sqlite_handler import SqliteHandler


class MyLogger(logging.Logger):
    """This class represents the logger for the application."""

    def __init__(
        self,
        name: str,
        log_file: Path,
        level: int = logging.INFO,
        log_to_console: bool = True,
        log_to_file: bool = True,
        log_to_database: bool = True,
        database: Union[Database, str] = None,
    ):
        """Initialize the logger."""
        super().__init__(name, level)
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create a file handler to write to the log file
        self.file_handler = None
        if log_to_file:
            self.file_handler = logging.FileHandler(self.log_file)
            self.file_handler.setLevel(level)
            self.file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            self.file_handler.setFormatter(self.file_formatter)
            self.addHandler(self.file_handler)
            self.info("File logging enabled")

        # Create a stream handler to print to stdout
        self.stream_handler = None
        if log_to_console:
            self.stream_handler = logging.StreamHandler()
            self.stream_handler.setLevel(level)
            self.stream_formatter = logging.Formatter("%(message)s")
            self.stream_handler.setFormatter(self.stream_formatter)
            self.addHandler(self.stream_handler)
            self.info("Console logging enabled")

        # Create a database handler to write to a database
        self.database = None
        if log_to_database:
            if database:
                if isinstance(database, Database):
                    self.database = database
                elif isinstance(database, str):
                    database_path = Path(database)
                    self.database = Database(database_path)
                else:
                    raise TypeError("database must be a Database or str")
            else:
                DEFAULT_DATABASE = "database/logging.db"
                database_path = Path(DEFAULT_DATABASE)
                database_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    self.database = Database(database_path)
                except Exception as exeption:
                    self.warning(
                        "Unable to open database at %s: %s",
                        database_path,
                        exeption
                    )
                    # Create an empty database object
                    self.database = Database(":memory:")
                    self.database = None

            self.database = database
            self.sqlite_handler = SqliteHandler(self.database)
            self.sqlite_handler.setLevel(level)
            self.addHandler(self.sqlite_handler)
            self.info("Database logging enabled")

        self.info("Logger initialized")

    def close(self):
        """Close the logger."""
        self.file_handler.close()
        self.stream_handler.close()
        self.sqlite_handler.close()
        self.removeHandler(self.file_handler)
        self.removeHandler(self.stream_handler)
        self.removeHandler(self.sqlite_handler)
        self.info("Logger closed")