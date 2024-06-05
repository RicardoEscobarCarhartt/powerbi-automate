"""This module contains unit tests for the my_logger module."""

from pathlib import Path
import logging
from unittest.mock import Mock

import pytest

from carhartt_pbi_automate.my_logger import MyLogger


@pytest.mark.unit
def test_my_logger(_initial_database_script, _log_file, _database):
    """Test the MyLogger class."""
    # Create a logger with the factory fixture
    logger = MyLogger(
        name="test_logger",
        log_file=_log_file,
        level=logging.DEBUG,
        log_to_console=False,
        log_to_file=False,
        log_to_database=False,
        initial_database_script=_initial_database_script,
        database=_database,
    )
    assert logger.name == "test_logger"
    assert logger.level == logging.DEBUG
    assert logger.log_file == _log_file
    assert logger.file_handler is None
    assert logger.stream_handler is None
    assert logger.database is None


@pytest.mark.unit
def test_my_logger_file(_initial_database_script, _log_file, _database):
    """Test the MyLogger class with log_to_file=True."""
    # Create a logger with the factory fixture
    logger = MyLogger(
        name="test_logger",
        log_file=_log_file,
        level=logging.DEBUG,
        log_to_console=False,
        log_to_file=True,
        log_to_database=False,
        initial_database_script=_initial_database_script,
        database=_database,
    )
    assert logger.name == "test_logger"
    assert logger.level == logging.DEBUG
    assert logger.log_file == _log_file
    assert logger.file_handler is not None
    assert logger.stream_handler is None
    assert logger.database is None


@pytest.mark.unit
def test_my_logger_console(_initial_database_script, _log_file, _database):
    """Test the MyLogger class with log_to_console=True."""
    # Create a logger with the factory fixture
    logger = MyLogger(
        name="test_logger",
        log_file=_log_file,
        level=logging.DEBUG,
        log_to_console=True,
        log_to_file=False,
        log_to_database=False,
        initial_database_script=_initial_database_script,
        database=_database,
    )
    assert logger.name == "test_logger"
    assert logger.level == logging.DEBUG
    assert logger.log_file == _log_file
    assert logger.file_handler is None
    assert logger.stream_handler is not None
    assert logger.database is None


@pytest.mark.unit
def test_my_logger_database(_initial_database_script, _log_file, _database):
    """Test the MyLogger class with log_to_database=True."""
    # Create a logger with the factory fixture
    logger = MyLogger(
        name="test_logger",
        log_file=_log_file,
        level=logging.DEBUG,
        log_to_console=False,
        log_to_file=False,
        log_to_database=True,
        initial_database_script=_initial_database_script,
        database=_database,
    )
    assert logger.name == "test_logger"
    assert logger.level == logging.DEBUG
    assert logger.log_file == _log_file
    assert logger.file_handler is None
    assert logger.stream_handler is None
    assert logger.database is not None
    assert "log_record" in logger.database.get_tables()


@pytest.mark.parametrize(
    "log_to_console, log_to_file, log_to_database",
    [
        (True, False, False),
        (False, True, False),
        (False, False, True),
        (True, True, False),
        (True, False, True),
        (False, True, True),
        (True, True, True),
    ],
)
@pytest.mark.unit
def test_close(
    _initial_database_script,
    _log_file,
    _database,
    log_to_console,
    log_to_file,
    log_to_database,
):
    """Test the close method."""
    # Create a logger with the factory fixture
    logger = MyLogger(
        name="test_logger",
        log_file=_log_file,
        level=logging.DEBUG,
        log_to_console=log_to_console,
        log_to_file=log_to_file,
        log_to_database=log_to_database,
        initial_database_script=_initial_database_script,
        database=_database,
    )
    # Mock the self.sqlite_handler.close() method
    if logger.sqlite_handler:
        logger.sqlite_handler.close = Mock()
    if logger.file_handler:
        logger.file_handler.close = Mock()
    if logger.stream_handler:
        logger.stream_handler.close = Mock()

    # Call the close method
    logger.close()

    # Assert the close method was called
    if log_to_database:
        logger.sqlite_handler.close.assert_called_once()
    if log_to_file:
        logger.file_handler.close.assert_called_once()
    if log_to_console:
        logger.stream_handler.close.assert_called_once()
