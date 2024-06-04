"""This module contains unit tests for the get_formated_duration module."""

import logging

import pytest


@pytest.mark.unit
def test_get_logger(
    logger: logging.Logger, project_root
):  # pylint: disable=W0621
    """Test the get_logger function."""
    # test with a logger name
    actual = logger.name
    # The expected value is the name of the logger that was passed to the
    # `tests\fixtures\get_logger.py` fixture.
    expected = "test_logger"
    assert actual == expected

    # test with a logger level
    actual = logger.level
    expected = logging.DEBUG
    assert actual == expected

    # test with a logger file handler
    for handler in logger.handlers:
        if type(logging.FileHandler) == type(handler):  # pylint: disable=C0123
            actual = handler.baseFilename
            expected = project_root / "test_logger.log"
            assert actual == str(expected)

    # test with a logger console handler
    for handler in logger.handlers:
        # Check if the handler is a console handler. I'm using type() instead
        # of isinstance() because I want to check the exact class and avoid
        # logging.FileHandler subclass objects from triggering the test.
        if type(handler) == logging.StreamHandler:  # pylint: disable=C0123
            assert handler.level == logging.INFO


@pytest.mark.unit
def test_get_logger_no_console_output(
    logger_no_console_output: logging.Logger,
):
    """Test the get_logger function with no console output."""
    # test with a logger console handler
    for handler in logger_no_console_output.handlers:
        # Check if the handler is a console handler. I'm using type() instead
        # of isinstance() because I want to check the exact class and avoid
        # logging.FileHandler subclass objects from triggering the test.
        if type(handler) == logging.StreamHandler:  # pylint: disable=C0123
            pytest.fail("Console handler should not be created.")


@pytest.mark.unit
def test_touch_file(_touch_file):
    """Test the touch_file function."""
    # The name of the file was created by the _touch_file fixture, from the
    # `tests\fixtures\get_logger.py` file.
    # Check if the file was created and the column names were written to it.
    expected = "asctime|name|levelname|message"
    with open(_touch_file, "r", encoding="utf-8") as file:
        actual = file.readline().strip()
        assert actual == expected
