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
        database: Union[Database, Path, str] = None,
        initial_database_script: Union[str, Path] = "database/logging.sql",
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

        # Validate the initial_database_script argument
        if isinstance(initial_database_script, str):
            initial_database_script = Path(initial_database_script)
        if not isinstance(initial_database_script, Path):
            raise TypeError(
                (
                    f"initial_database_script must be a Path or str,"
                    f" not {type(initial_database_script)}"
                )
            )
        if not initial_database_script.exists():
            raise FileNotFoundError(
                f"initial_database_script not found at {initial_database_script}"
            )
        else:
            self.initial_database_script = initial_database_script

        # Create a database handler to write to a database
        self.database = None
        if log_to_database:
            if database:
                if isinstance(database, Database):
                    self.database = database
                elif isinstance(database, str):
                    database_path = Path(database)
                    self.database = Database(database_path)
                    # Check if database file exists and contains the correct
                    # table "log_record"
                    if not self.database.table_exists("log_record"):
                        self.database.close()
                        self.database = Database(
                            database_path, self.initial_database_script
                        )
                elif isinstance(database, Path):
                    self.database = Database(database, self.initial_database_script)
                    # Create the database file if it does not exist
                    if not database.exists():
                        database.parent.mkdir(parents=True, exist_ok=True)
                        self.database = Database(database)
                else:
                    raise TypeError("database must be a Database or str")
            else:
                default_database = "database/logging.db"
                database_path = Path(default_database)
                database_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    self.database = Database(database_path)
                except FileNotFoundError as exception:
                    self.warning(
                        "Unable to open database at %s: %s",
                        database_path,
                        exception,
                    )
                    # Create an empty database object
                    self.database = Database(":memory:")

            # Create a database handler
            self.sqlite_handler = SqliteHandler(self.database)
            self.sqlite_handler.setLevel(level)
            self.addHandler(self.sqlite_handler)
            self.info("Database logging enabled")

        self.info("Logger initialized")

    def close(self):
        """Close the logger."""
        if self.file_handler:
            self.file_handler.close()
            self.removeHandler(self.file_handler)
        if self.stream_handler:
            self.stream_handler.close()
            self.removeHandler(self.stream_handler)
        if self.sqlite_handler:
            self.sqlite_handler.close()
            self.removeHandler(self.sqlite_handler)
        self.info("Logger closed")
