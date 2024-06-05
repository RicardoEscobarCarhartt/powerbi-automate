"""This module contains tests for the sqlite_handler module."""

import logging

import pytest

from carhartt_pbi_automate.sqlite_handler import SqliteHandler


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
def test_sqlite_handler_init_with_database(
    database_file, sql_script
):  # pylint: disable=W0621
    """Test the SqliteHandler __init__ method with a Database object."""
    handler = SqliteHandler(database=database_file, sql_script=sql_script)

    assert handler.database is database_file


@pytest.mark.unit
def test_sqlite_handler_init_with_inserted_record(
    database_file, sql_script
):  # pylint: disable=W0621
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
