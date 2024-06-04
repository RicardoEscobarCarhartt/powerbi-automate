"""Fixtures for the get_logger module."""

from pathlib import Path
import logging

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
