"""This module contains unit tests for the get_formated_duration module."""

import logging
from pathlib import Path

import pytest

from carhartt_pbi_automate.get_logger import get_logger


@pytest.fixture(scope="function")
def logger():
    """Return a logger name."""
    logger = get_logger("test_logger")  # pylint: disable=W0621
    yield logger
    # teardown
    # ensure all logging resources are released
    logging.shutdown()
    Path("test_logger.log").unlink(missing_ok=True)


@pytest.mark.unit
def test_get_logger(
    logger: logging.Logger, project_root
):  # pylint: disable=W0621
    """Test the get_logger function."""
    # test with a logger name
    actual = logger.name
    expected = "test_logger"
    assert actual == expected

    # test with a logger level
    actual = logger.level
    expected = logging.DEBUG
    assert actual == expected

    # test with a logger file handler
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
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
