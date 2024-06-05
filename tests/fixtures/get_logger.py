"""Fixtures for the get_logger module."""

from pathlib import Path
import logging

import pytest

from carhartt_pbi_automate.get_logger import get_logger, touch_file


@pytest.fixture(scope="function")
def logger():
    """Return a logger name."""
    logger_instance = get_logger("test_logger")  # pylint: disable=W0621
    yield logger_instance
    # teardown
    # ensure all logging resources are released
    logging.shutdown()
    Path("test_logger.log").unlink(missing_ok=True)


@pytest.fixture(scope="function")
def logger_no_console_output():
    """Return a logger name."""
    logger_no_console_output_instance = get_logger(
        "test_logger_no_console_output", console_output=False
    )
    yield logger_no_console_output_instance
    # teardown
    # ensure all logging resources are released
    logging.shutdown()
    Path("test_logger_no_console_output.log").unlink(missing_ok=True)


@pytest.fixture(scope="function")
def _touch_file(project_root):
    """Return a touch file."""
    logfile = project_root / "test.log"
    columns = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
    touch_file_instance = touch_file(logfile, columns)
    yield touch_file_instance
    # teardown
    Path(logfile).unlink(missing_ok=True)