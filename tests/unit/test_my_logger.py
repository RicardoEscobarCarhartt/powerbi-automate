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

@pytest.mark.unit
def  test_close(_initial_database_script, _log_file, _database):
    """Test the close method."""
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
    logger.close()
    # Mock the close method of the database
    # TODO mock the close method of the database, file_handler, and stream_handler