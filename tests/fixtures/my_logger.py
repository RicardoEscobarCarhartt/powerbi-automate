"""Fixtures for the my_logger module."""

from pathlib import Path
from typing import Generator
import logging

import pytest

from carhartt_pbi_automate.my_logger import MyLogger
from carhartt_pbi_automate.database import Database


@pytest.fixture(scope="function")
def _initial_database_script(
    project_root: Path,
) -> Generator[Path, None, None]:
    """Return the initial database script."""
    filepath = project_root / "database" / "logging_test.sql"

    # Create the parent directory if it does not exist
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Write the initial database script
    sql = """CREATE TABLE IF NOT EXISTS log_record (id INTEGER PRIMARY KEY AUTOINCREMENT,
    args TEXT, -- The tuple of arguments merged into msg to produce message, or a dict whose values are used for the merge (when there is only one argument, and it is a dictionary).
    asctime TEXT, -- Human-readable time when the LogRecord was created. By default this is of the form ‘2003-07-08 16:49:45,896’ (the numbers after the comma are millisecond portion of the time) asctime is local timezone where the database is running.
    asctime_utc TEXT, -- UTC time zone version of asctime
    created REAL, -- Time when the LogRecord was created (as returned by time.time()).
    exc_info TEXT, -- Exception tuple (à la sys.exc_info) or, if no exception has occurred, None.
    filename TEXT, -- Filename portion of pathname.
    funcName TEXT, -- Name of function containing the logging call.
    levelname TEXT, -- Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
    lineno INTEGER, -- Source line number where the logging call was issued (if available).
    message TEXT, -- The logged message, computed as msg % args. This is set when Formatter.format() is invoked.
    module TEXT, -- Module (name portion of filename).
    msecs REAL, -- Millisecond portion of the time when the LogRecord was created.
    msg TEXT, -- The format string passed in the original logging call. Merged with args to produce message, or an arbitrary object (see Using arbitrary objects as messages).
    name TEXT, -- Name of the logger used to log the call.
    pathname TEXT, -- Full pathname of the source file where the logging call was issued (if available).
    process INTEGER, -- Process ID (if available).
    processName TEXT, -- Process name (if available).
    relativeCreated REAL, -- Time in milliseconds when the LogRecord was created, relative to the time the logging module was loaded.
    stack_info TEXT, -- Stack frame information (where available) from the bottom of the stack in the current thread, up to and including the stack frame of the logging call which resulted in the creation of this record.
    thread INTEGER, -- Thread ID (if available).
    threadName TEXT, -- Thread name (if available).
    taskName TEXT -- asyncio.Task name (if available).
    );
    """

    # Write the SQL script to the file
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(sql)

    yield filepath
    # Clean up the file
    filepath.unlink(missing_ok=True)


@pytest.fixture(scope="function")
def _log_file() -> Generator[Path, None, None]:
    """Return a log file."""
    filepath = Path("test_logger.log")

    yield filepath
    # Clean up the file
    filepath.unlink(missing_ok=True)


@pytest.fixture(scope="function")
def _database() -> Generator[Database, None, None]:
    """Return a database."""
    database = Path("test_logger.db")
    yield database
    # Clean up the database
    database.unlink(missing_ok=True)