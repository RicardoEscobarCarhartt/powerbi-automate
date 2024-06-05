"""This module contains tests for the sqlite_handler module."""

from unittest.mock import patch
from pathlib import Path
import logging

import pytest

from carhartt_pbi_automate.sqlite_handler import SqliteHandler
from carhartt_pbi_automate.database import Database


@pytest.fixture(scope="function")
def sql_script():
    """Return a SQL script."""
    sql = """CREATE TABLE log_record (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        args            TEXT, -- The tuple of arguments merged into msg to produce message, or a dict whose values are used for the merge (when there is only one argument, and it is a dictionary).
        asctime         TEXT, -- Human-readable time when the LogRecord was created. By default this is of the form ‘2003-07-08 16:49:45,896’ (the numbers after the comma are millisecond portion of the time) asctime is local timezone where the database is running.
        asctime_utc     TEXT, -- UTC time zone version of asctime
        created         REAL, -- Time when the LogRecord was created (as returned by time.time()).
        exc_info        TEXT, -- Exception tuple (à la sys.exc_info) or, if no exception has occurred, None.
        filename        TEXT, -- Filename portion of pathname.
        funcName        TEXT, -- Name of function containing the logging call.
        levelname       TEXT, -- Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        lineno          INTEGER, -- Source line number where the logging call was issued (if available).
        message         TEXT, -- The logged message, computed as msg % args. This is set when Formatter.format() is invoked.
        module          TEXT, -- Module (name portion of filename).
        msecs           REAL, -- Millisecond portion of the time when the LogRecord was created.
        msg             TEXT, -- The format string passed in the original logging call. Merged with args to produce message, or an arbitrary object (see Using arbitrary objects as messages).
        name            TEXT, -- Name of the logger used to log the call.
        pathname        TEXT, -- Full pathname of the source file where the logging call was issued (if available).
        process         INTEGER, -- Process ID (if available).
        processName     TEXT, -- Process name (if available).
        relativeCreated REAL, -- Time in milliseconds when the LogRecord was created, relative to the time the logging module was loaded.
        stack_info      TEXT, -- Stack frame information (where available) from the bottom of the stack in the current thread, up to and including the stack frame of the logging call which resulted in the creation of this record.
        thread          INTEGER, -- Thread ID (if available).
        threadName      TEXT, -- Thread name (if available).
        taskName        TEXT -- asyncio.Task name (if available).
    );
    """

    # Path to the SQL script
    path = Path("test_sql_script.sql")

    # Create a file with the SQL script
    with open(path, "w", encoding="utf-8") as file:
        file.write(sql)

    yield path
    # Remove the file
    logging.shutdown()
    path.unlink(missing_ok=True)


@pytest.fixture(scope="function")
def database_file(sql_script):  # pylint: disable=W0621
    """Return a Database object."""
    path = Path("test_sqlite_handler.db")

    yield Database(path, sql_script)
    # Remove the file
    logging.shutdown()
    path.unlink(missing_ok=True)


@pytest.mark.unit
def test_sqlite_handler_init():
    """Test the SqliteHandler __init__ method."""
    with pytest.raises(TypeError):
        SqliteHandler()

    with pytest.raises(TypeError):
        SqliteHandler(database="database")

    with pytest.raises(TypeError):
        SqliteHandler(sql_script="sql_script")

    with pytest.raises(TypeError):
        SqliteHandler(database="database", sql_script="sql_script")


@pytest.mark.unit
def test_sqlite_handler_emit():
    """Test the SqliteHandler emit method."""
    with pytest.raises(TypeError):
        handler = SqliteHandler()
        handler.emit("record")


@pytest.mark.unit
def test_sqlite_handler_init_with_database(database_file, sql_script):  # pylint: disable=W0621
    """Test the SqliteHandler __init__ method with a Database object."""
    handler = SqliteHandler(database=database_file, sql_script=sql_script)

    assert handler.database is database_file


@pytest.mark.unit
def test_sqlite_handler_init_with_inserted_record(database_file, sql_script):  # pylint: disable=W0621
    """Test the SqliteHandler __init__ method with a Database object."""
    handler = SqliteHandler(database=database_file, sql_script=sql_script)

    # Create a record
    record = logging.LogRecord(
        name="name",
        level=logging.INFO,
        pathname="pathname",
        lineno=1,
        msg="msg",
        args=None,
        exc_info=None,
    )

    # Emit the record
    handler.emit(record)
